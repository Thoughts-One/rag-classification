import redis
from datetime import timedelta
from typing import Dict, Optional
import json
import os

class ClassificationCache:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client = redis.Redis.from_url(redis_url)
        self.ttl = timedelta(hours=int(os.getenv("CACHE_TTL_HOURS", "24")))

    def get(self, key: str) -> Optional[Dict]:
        """Get cached classification result"""
        cached = self.client.get(key)
        if cached:
            return json.loads(cached)
        return None

    def set(self, key: str, value: Dict) -> None:
        """Cache classification result"""
        self.client.setex(
            name=key,
            time=self.ttl,
            value=json.dumps(value)
        )

    def clear(self, pattern: str = "*") -> int:
        """Clear cache entries matching pattern"""
        keys = self.client.keys(pattern)
        if keys:
            return self.client.delete(*keys)
        return 0