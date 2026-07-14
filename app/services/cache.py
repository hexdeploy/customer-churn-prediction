import os
import json
import hashlib
from redis import asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

class CacheEngine:
    def __init__(self):
        print("⚡ Initializing Async Aioredis pooling structure...")
        self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)

    def _generate_hash(self, input_features: dict) -> str:
        """Hashes raw inputs consistently to form an optimized deterministic lookup string[cite: 1]."""
        # Sort keys to ensure the same dictionary structures compute to the exact same hash signature
        serialized_features = json.dumps(input_features, sort_keys=True)
        return hashlib.sha256(serialized_features.encode('utf-8')).hexdigest()

    async def get_cached_prediction(self, input_features: dict) -> float:
        """Retrieves a cached churn probability score if signature matches[cite: 1]."""
        try:
            key_hash = self._generate_hash(input_features)
            cached_val = await self.redis.get(f"churn_cache:{key_hash}")
            return float(cached_val) if cached_val else None
        except Exception:
            return None

    async def set_prediction_cache(self, input_features: dict, score: float, ttl_seconds: int = 3600):
        """Caches computed model weights by feature hash structure for exactly 1 hour[cite: 1]."""
        try:
            key_hash = self._generate_hash(input_features)
            await self.redis.set(f"churn_cache:{key_hash}", str(score), ex=ttl_seconds)
        except Exception as e:
            print(f"⚠️ Caching allocation missed: {e}")