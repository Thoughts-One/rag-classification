import os
import json
import httpx
from typing import Dict, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenRouterClient:
    """Client for interacting with OpenRouter API with support for multiple models."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required. Please set it in your .env file.\n"
                "Get a key from https://openrouter.ai/keys"
            )
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Model configuration - primary and fallbacks
        self.models = {
            "primary": "deepseek/deepseek-chat-v3",
            "fallbacks": [
                "anthropic/claude-3-opus",
                "anthropic/claude-3-sonnet",
                "openai/gpt-4-turbo-preview"
            ]
        }
        
        self.default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://rag-classification.onrender.com",
            "X-Title": "RAG Classification Service"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def classify(
        self,
        content: str,
        role: Optional[str] = None,
        model: Optional[str] = None,
        title: str = "",
        url: str = "",
        source: str = ""
    ) -> Dict:
        """Classify content using specified model or fallback strategy."""
        model = model or self.models["primary"]
        models_to_try = [model] + self.models["fallbacks"]
        
        for current_model in models_to_try:
            try:
                return await self._classify_with_model(content, role, current_model, title, url, source)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    print(f"Model {current_model} failed: 401 Unauthorized. Please check your OPENROUTER_API_KEY for validity.")
                else:
                    print(f"Model {current_model} failed with HTTP error: {e.response.status_code} - {e.response.text}")
                continue # Try next fallback model
            except Exception as e:
                print(f"Model {current_model} failed with unexpected error: {str(e)}")
                continue # Try next fallback model
                
        raise Exception("All model attempts failed. Please ensure your API keys are valid and check network connectivity.")

    async def _classify_with_model(
        self,
        content: str,
        role: Optional[str],
        model: str,
        title: str = "",
        url: str = "",
        source: str = ""
    ) -> Dict:
        """Perform classification with a specific model."""
        prompt = self._build_prompt(content, role, title, url, source)
        
        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": prompt
            }],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.base_url,
                json=payload,
                headers=self.default_headers
            )
            response.raise_for_status()
            result = response.json()
            
            content = result["choices"][0]["message"]["content"]
            return self._parse_classification_response(content, model)

    def _parse_classification_response(self, content: str, model: str) -> Dict:
        """Parse the LLM response into structured classification data."""
        try:
            # Remove markdown code block fences if present
            if content.startswith("```json") and content.endswith("```"):
                content = content[len("```json"): -len("```")].strip()
            
            result = json.loads(content)
            return {
                "section_hierarchy": result.get("section_hierarchy", []),
                "tags": result.get("tags", []),
                "refined_source": result.get("refined_source", ""),
                "collection": result.get("collection", ""),
                "topics": result.get("topics", []),
                "confidence": result.get("confidence", 0.0),
                "model_used": model
            }
        except json.JSONDecodeError:
            return {
                "section_hierarchy": [],
                "tags": [],
                "refined_source": "",
                "collection": "",
                "topics": [],
                "confidence": 0.0,
                "model_used": model
            }

    def _build_prompt(self, content: str, role: Optional[str], title: str = "", url: str = "", source: str = "") -> str:
        """Build classification prompt with pre-classification requirements, including taxonomy."""
        # Load taxonomy dynamically within the method to ensure it's always fresh
        from core.classifier import TAXONOMY
        
        collections_prompt = ""
        for col_name, col_data in TAXONOMY.get("collections", {}).items():
            collections_prompt += f"\n- Collection: {col_name}\n  Description: {col_data.get('description', 'N/A')}\n  Topics: {', '.join(col_data.get('topics', []))}\n  Tags: {', '.join(col_data.get('tags', []))}"

        base_prompt = f"""
        You are a document classification system for technical documentation. Your task is to analyze the provided content and classify it based on the given taxonomy.
        
        Return your classification as a JSON object with the following keys:
        - `section_hierarchy`: A list of strings representing the hierarchical section structure (e.g., ["API Reference", "Authentication"]). If no clear hierarchy, return an empty list.
        - `tags`: A list of 3-5 relevant tags (lowercase, hyphenated). If fewer than 3 or no tags are relevant, return what is applicable or an empty list.
        - `refined_source`: A more specific classification of the source than the input `source` (e.g., "wordpress-coding-standards-changelog"). If no refinement is possible, return an empty string.
        - `collection`: The most relevant collection from the provided taxonomy (e.g., "wordpress_block_development"). If no collection matches, return an empty string.
        - `topics`: A list of relevant topics from the chosen collection. If no topics match, return an empty list.
        - `confidence`: A float between 0.0 and 1.0 indicating your confidence in the classification.
        - `model_used`: The name of the model used for classification.

        If you cannot find a suitable classification, return an empty JSON structure for the classification fields, but always ensure the output is valid JSON.

        Available Collections (Taxonomy):
        {collections_prompt}

        Document Details:
        - Title: {title}
        - Source: {source}
        - URL: {url}
        - Content (first 2000 chars): {content[:2000] + '...' if len(content) > 2000 else content}

        """
        
        if role == "CODE":
            return base_prompt + """
            Additional classification focus for 'CODE' role:
            - Implementation details, code quality, production readiness.
            """
        elif role == "ARCHITECT":
            return base_prompt + """
            Additional classification focus for 'ARCHITECT' role:
            - System design patterns, architectural considerations, integration points.
            """
        else:
            return base_prompt + """
            Provide a comprehensive classification of the content based on the taxonomy.
            """