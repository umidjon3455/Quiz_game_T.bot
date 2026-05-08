"""
Redis client configuration and utilities.
"""

import redis.asyncio as redis
from typing import Any, Optional
import json
from config import settings


class RedisClient:
    """Redis client wrapper with async support."""
    
    def __init__(self):
        self._client: Optional[redis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis."""
        self._client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self._client:
            await self._client.close()
    
    @property
    def client(self) -> redis.Redis:
        """Get Redis client (ensure connection)."""
        if self._client is None:
            raise RuntimeError("Redis client not connected. Call connect() first.")
        return self._client
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> None:
        """Set a key-value pair in Redis."""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        await self.client.set(key, value, ex=expire)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis."""
        value = await self.client.get(key)
        if value is None:
            return None
        
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def delete(self, key: str) -> None:
        """Delete a key from Redis."""
        await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis."""
        return bool(await self.client.exists(key))
    
    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value."""
        return await self.client.incrby(key, amount)
    
    async def expire(self, key: str, seconds: int) -> None:
        """Set expiration for a key."""
        await self.client.expire(key, seconds)


# Global Redis client instance
redis_client = RedisClient()
