import math
import time
from typing import Dict, Optional, Tuple

from storage.redis_simulator import RedisSimulator


class SlidingWindowCounter:
    WINDOW_TTL_MULTIPLIER = 2

    def __init__(
        self,
        redis_client: RedisSimulator,
        request_limit: int,
        window_size_seconds: int
    ) -> None:

        self.redis = redis_client
        self.request_limit = request_limit
        self.window_size_seconds = window_size_seconds

    def _build_window_keys(
        self,
        client_id: str,
        timestamp: float
    ) -> Tuple[str, str]:

        current_window_id = math.floor(
            timestamp / self.window_size_seconds
        )

        previous_window_id = current_window_id - 1

        current_window_key = (
            f"{client_id}:{current_window_id}"
        )

        previous_window_key = (
            f"{client_id}:{previous_window_id}"
        )

        return (
            current_window_key,
            previous_window_key
        )

    async def _get_counter_value(
        self,
        redis_key: str
    ) -> int:

        stored_value = await self.redis.get(
            redis_key
        )

        return int(stored_value or 0)

    def _calculate_weighted_count(
        self,
        previous_window_count: int,
        current_window_count: int,
        timestamp: float
    ) -> int:

        current_window_progress = (

            timestamp %
            self.window_size_seconds

        ) / self.window_size_seconds

        weighted_count = (

            previous_window_count *
            (1 - current_window_progress)

        ) + current_window_count

        return math.ceil(
            weighted_count
        )

    async def is_allowed(
        self,
        client_id: str,
        current_time: Optional[float] = None
    ) -> Dict:

        request_timestamp = (
            current_time
            if current_time is not None
            else time.time()
        )

        (
            current_window_key,
            previous_window_key
        ) = self._build_window_keys(

            client_id,

            request_timestamp
        )

        previous_window_count = await self._get_counter_value(
            previous_window_key
        )

        current_window_count = await self._get_counter_value(
            current_window_key
        )

        effective_request_count = (

            self._calculate_weighted_count(

                previous_window_count,

                current_window_count,

                request_timestamp
            )
        )

        if effective_request_count >= self.request_limit:

            retry_after_seconds = (

                self.window_size_seconds -

                (
                    request_timestamp %
                    self.window_size_seconds
                )
            )

            return {

                "allowed": False,

                "retry_after": round(
                    retry_after_seconds,
                    2
                ),

                "remaining": 0
            }

        updated_counter = await self.redis.incr(
            current_window_key
        )

        await self.redis.expire(

            current_window_key,

            self.window_size_seconds *
            self.WINDOW_TTL_MULTIPLIER
        )

        remaining_requests = max(

            0,

            self.request_limit -

            effective_request_count -

            1
        )

        return {

            "allowed": True,

            "retry_after": 0,

            "remaining": remaining_requests,

            "count": updated_counter
        }
    