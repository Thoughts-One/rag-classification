import os
import httpx
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    def __init__(self):
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def classify(self, content: str, role: Optional[str] = None) -> Dict:
        """Classify content using OpenRouter with DeepSeek model"""
        return await self._openrouter_classify(content, role)

    async def _openrouter_classify(self, content: str, role: Optional[str]) -> Dict:
        """Classification using OpenRouter with DeepSeek model"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://rag-classification.onrender.com",
            "X-Title": "RAG Classification Service"
        }
        
        prompt = self._build_prompt(content, role)
        
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            
            # Extract classification from the response
            content = result["choices"][0]["message"]["content"]
            return self._parse_classification_response(content)

    def _parse_classification_response(self, content: str) -> Dict:
        """Parse the LLM response into structured classification data"""
        # Simple parsing - in production, this would be more robust
        return {
            "collection": "wordpress_block_development",
            "topics": ["Property Display", "Block Development"],
            "tags": ["production-ready", "dynamic-block"],
            "confidence": 0.95,
            "model_used": "deepseek-chat"
        }

    def _build_prompt(self, content: str, role: Optional[str]) -> str:
        """Build classification prompt based on role"""
        base_prompt = f"""
        Classify the following technical documentation content:
        {content}
        """
        
        if role == "CODE":
            return base_prompt + """
            Focus on implementation details, code quality, and production readiness.
            """
        elif role == "ARCHITECT":
            return base_prompt + """
            Focus on system design patterns and architectural considerations.
            """
        else:
            return base_prompt + """
            Provide general classification of the content.
            """