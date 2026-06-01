import pytest

from algorithms.sliding_window import (
    SlidingWindowCounter
)

from storage.redis_simulator import (
    RedisSimulator
)


@pytest.mark.asyncio
async def test_should_throttle_burst_traffic():

    redis_client = RedisSimulator(
        latency_ms=0
    )

    limiter = SlidingWindowCounter(

        redis_client=redis_client,

        request_limit=100,

        window_size_seconds=1
    )

    allowed_requests = 0

    blocked_requests = 0

    for _ in range(1000):

        response = await limiter.is_allowed(
            "burst_client"
        )

        if response["allowed"]:

            allowed_requests += 1

        else:

            blocked_requests += 1

    assert allowed_requests <= 100

    assert blocked_requests >= 900
