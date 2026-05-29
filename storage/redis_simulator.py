import asyncio
import time
from typing import Optional, Dict, Union

class RedisSimulator:
    """
    A thread-safe, asynchronous simulator for Redis to be used in the 
    Senior Backend Challenge. This helps simulate network latency and 
    distributed state management.
    """
    def __init__(self, latency_ms: int = 50):
        self.latency_sec = latency_ms / 1000.0
        self._data: Dict[str, str] = {}
        self._ttls: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def _simulate_latency(self):
        await asyncio.sleep(self.latency_sec)

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            await self._simulate_latency()
            # Check for expiration
            if key in self._ttls and time.time() > self._ttls[key]:
                del self._data[key]
                del self._ttls[key]
                return None
            return self._data.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None):
        async with self._lock:
            await self._simulate_latency()
            self._data[key] = value
            if ex:
                self._ttls[key] = time.time() + ex

    async def incr(self, key: str) -> int:
        """Atomic increment operation."""
        async with self._lock:
            await self._simulate_latency()
            val = int(self._data.get(key, 0))
            val += 1
            self._data[key] = str(val)
            return val

    async def expire(self, key: str, seconds: int):
        async with self._lock:
            await self._simulate_latency()
            if key in self._data:
                self._ttls[key] = time.time() + seconds

    async def delete(self, key: str):
        async with self._lock:
            await self._simulate_latency()
            self._data.pop(key, None)
            self._ttls.pop(key, None)

    async def pipeline(self):
        """Simple pipeline implementation for atomic batching."""
        return RedisPipeline(self)

class RedisPipeline:
    def __init__(self, simulator: RedisSimulator):
        self.simulator = simulator
        self.commands = []

    def get(self, key: str):
        self.commands.append(('get', (key,)))
        return self

    def incr(self, key: str):
        self.commands.append(('incr', (key,)))
        return self

    def expire(self, key: str, seconds: int):
        self.commands.append(('expire', (key, seconds)))
        return self

    async def execute(self) -> list:
        results = []
        # In a real pipeline, we'd execute these together
        for cmd, args in self.commands:
            method = getattr(self.simulator, cmd)
            results.append(await method(*args))
        return results
    