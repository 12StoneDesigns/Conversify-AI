"""LRU Cache implementation for response caching."""

from typing import Dict, Optional, Any

class LRUCache:
    """Least Recently Used (LRU) cache implementation."""
    
    def __init__(self, maxsize: int = 100):
        """Initialize LRU cache with specified maximum size."""
        self.cache: Dict[str, Any] = {}
        self.maxsize = maxsize
        self.hits = 0
        self.misses = 0
        
    def get(self, key: str) -> Optional[str]:
        """
        Get an item from the cache.
        
        Args:
            key: Cache key to retrieve
            
        Returns:
            The cached value if found, None otherwise
        """
        if key in self.cache:
            self.hits += 1
            value = self.cache.pop(key)
            self.cache[key] = value  # Move to end (most recently used)
            return value
        self.misses += 1
        return None
        
    def put(self, key: str, value: str):
        """
        Add an item to the cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.maxsize:
            self.cache.pop(next(iter(self.cache)))  # Remove least recently used
        self.cache[key] = value
        
    def __setitem__(self, key: str, value: str):
        """Dictionary-style setter for cache items."""
        self.put(key, value)
        
    def __getitem__(self, key: str) -> str:
        """Dictionary-style getter for cache items."""
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value
        
    def get_stats(self) -> Dict[str, float]:
        """Get cache performance statistics."""
        total = self.hits + self.misses
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / total if total > 0 else 0
        }
