import asyncio
import math
import time

from typing import Any, Dict, Tuple

from config.constants import (
    WINDOW_TTL_MULTIPLIER
)

from storage.redis_simulator import (
    RedisSimulator
)


class SlidingWindowCounter:

    def __init__(
        self,
        redis_client: RedisSimulator,
        request_limit: int,
        window_size_seconds: int
    ):

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

        self._request_lock = (
            asyncio.Lock()
        )

    def _build_window_keys(
        self,
        client_id: str,
        current_time: float
    ):

        current_window = math.floor(

            current_time /

            self.window_size_seconds
        )

        previous_window = (
            current_window - 1
        )

        return (

            f"{client_id}:{current_window}",

            f"{client_id}:{previous_window}"
        )

    def _calculate_weighted_count(
        self,
        previous_count: int,
        current_count: int,
        current_time: float
    ):

        progress_ratio = (

            current_time %

            self.window_size_seconds

        ) / self.window_size_seconds

        weighted_count = (

            previous_count *

            (1 - progress_ratio)

        ) + current_count

        return math.ceil(
            weighted_count
        )

    async def is_allowed(
        self,
        client_id: str,
        current_time: float | None = None
    ):

        async with self._request_lock:

            request_time = (

                current_time

                if current_time is not None

                else time.time()
            )

            (
                current_key,

                previous_key

            ) = self._build_window_keys(

                client_id,

                request_time
            )

            previous_count = int(

                await self.redis.get(
                    previous_key
                )

                or 0
            )

            current_count = int(

                await self.redis.get(
                    current_key
                )

                or 0
            )

            effective_count = (

                self._calculate_weighted_count(

                    previous_count,

                    current_count,

                    request_time
                )
            )

            if effective_count >= self.request_limit:

                retry_after = round(

                    self.window_size_seconds -

                    (
                        request_time %

                        self.window_size_seconds
                    ),

                    2
                )

                return {

                    "allowed": False,

                    "retry_after": retry_after,

                    "remaining": 0
                }

            request_count = await self.redis.incr(
                current_key
            )

            await self.redis.expire(

                current_key,

                self.window_size_seconds *

                WINDOW_TTL_MULTIPLIER
            )

            remaining_requests = max(

                0,

                self.request_limit -

                effective_count -

                1
            )

            return {

                "allowed": True,

                "retry_after": 0,

                "remaining": remaining_requests,

                "count": request_count
            }

