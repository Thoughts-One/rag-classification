import os
import json
import httpx
from typing import Dict, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenRouterClient:
    """Client for interacting with OpenRouter API with support for multiple models."""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
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
            except Exception as e:
                print(f"Model {current_model} failed: {str(e)}")
                continue
                
        raise Exception("All model attempts failed")

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
        """Build classification prompt with pre-classification requirements."""
        base_prompt = f"""
        You are a document classification system for technical documentation. Analyze the provided content and return:
        1. A hierarchical section structure (e.g. ["API Reference", "Authentication"])
        2. 3-5 relevant tags (lowercase, hyphenated)
        3. A refined source classification (more specific than input)
        4. Role-specific classification (based on the role parameter)
        
        Document Title: {title}
        Source: {source}
        URL: {url}
        Content: {content[:2000] + '...' if len(content) > 2000 else content}
        """
        
        if role == "CODE":
            return base_prompt + """
            Additional focus on:
            - Implementation details
            - Code quality
            - Production readiness
            """
        elif role == "ARCHITECT":
            return base_prompt + """
            Additional focus on:
            - System design patterns
            - Architectural considerations
            - Integration points
            """
        else:
            return base_prompt + """
            Provide comprehensive classification of the content.
            """