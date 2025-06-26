from typing import Dict, Optional
from .openrouter_client import OpenRouterClient

class LLMClient:
    def __init__(self):
        self.client = OpenRouterClient()

    async def classify(self, content: str, role: Optional[str] = None) -> Dict:
        """Classify content using OpenRouter with DeepSeek model and fallbacks"""
        return await self.client.classify(content, role)