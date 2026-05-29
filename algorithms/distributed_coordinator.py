from threading import Lock
from typing import Any, Dict

from algorithms.sliding_window import (
    SlidingWindowCounter
)

from storage.redis_simulator import (
    RedisSimulator
)


class DistributedRateLimiter:

    def __init__(
        self,
        redis_client: RedisSimulator,
        request_limit: int,
        window_size_seconds: int
    ) -> None:

        if request_limit <= 0:

            raise ValueError(
                "request_limit must be positive"
            )

        if window_size_seconds <= 0:

            raise ValueError(
                "window_size_seconds must be positive"
            )

        self.redis = redis_client

        self.request_limit = (
            request_limit
        )

        self.window_size_seconds = (
            window_size_seconds
        )

        self.node_limiters: Dict[
            str,
            SlidingWindowCounter
        ] = {}

        self._lock = Lock()

    def register_node(
        self,
        node_id: str
    ) -> None:

        normalized_node_id = (
            node_id.strip()
        )

        if not normalized_node_id:

            raise ValueError(
                "node_id cannot be empty"
            )

        with self._lock:

            if normalized_node_id in self.node_limiters:

                raise ValueError(
                    "node already registered"
                )

            limiter = SlidingWindowCounter(

                redis_client=self.redis,

                request_limit=(
                    self.request_limit
                ),

                window_size_seconds=(
                    self.window_size_seconds
                )
            )

            self.node_limiters[
                normalized_node_id
            ] = limiter

    async def allow_request(
        self,
        node_id: str,
        client_id: str
    ) -> Dict[str, Any]:

        limiter = (
            self.node_limiters.get(
                node_id
            )
        )

        if limiter is None:

            raise ValueError(
                "unknown node"
            )

        return await limiter.is_allowed(
            client_id
        )

    def registered_nodes_count(
        self
    ) -> int:

        return len(
            self.node_limiters
        )
