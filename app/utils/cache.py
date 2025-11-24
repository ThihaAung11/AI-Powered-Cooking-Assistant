"""
Simple caching utility for LLM recommendations.
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import hashlib
import json


class SimpleCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl_minutes: int = 60):
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
    
    def _generate_key(self, **kwargs) -> str:
        """Generate cache key from kwargs."""
        # Sort to ensure consistent keys
        sorted_data = json.dumps(kwargs, sort_keys=True)
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, expiry = self._cache[key]
            if datetime.utcnow() < expiry:
                return value
            else:
                # Remove expired entry
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[timedelta] = None):
        """Set value in cache with TTL."""
        expiry = datetime.utcnow() + (ttl or self.default_ttl)
        self._cache[key] = (value, expiry)
    
    def clear(self):
        """Clear all cache."""
        self._cache.clear()
    
    def remove_expired(self):
        """Remove all expired entries."""
        now = datetime.utcnow()
        expired_keys = [k for k, (_, expiry) in self._cache.items() if now >= expiry]
        for key in expired_keys:
            del self._cache[key]


# Global cache instance
recommendation_cache = SimpleCache(default_ttl_minutes=30)  # Cache for 30 minutes
