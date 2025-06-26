import os
import httpx
from typing import Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMClient:
    def __init__(self):
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        self.max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def classify(self, content: str, role: Optional[str] = None) -> Dict:
        """Classify content using the primary LLM with fallback"""
        try:
            return await self._deepseek_classify(content, role)
        except Exception as e:
            print(f"DeepSeek classification failed: {e}, trying fallback")
            return await self._openrouter_classify(content, role)

    async def _deepseek_classify(self, content: str, role: Optional[str]) -> Dict:
        """Classify using DeepSeek API"""
        headers = {
            "Authorization": f"Bearer {self.deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = self._build_prompt(content, role)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/classify",
                json={"prompt": prompt},
                headers=headers
            )
            response.raise_for_status()
            return response.json()

    async def _openrouter_classify(self, content: str, role: Optional[str]) -> Dict:
        """Fallback classification using OpenRouter"""
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = self._build_prompt(content, role)
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/classify",
                json={"prompt": prompt},
                headers=headers
            )
            response.raise_for_status()
            return response.json()

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