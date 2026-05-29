import pytest

from algorithms.sliding_window import SlidingWindowCounter
from storage.redis_simulator import RedisSimulator


TEST_WINDOW_SIZE = 1


@pytest.fixture
def redis_client():

    return RedisSimulator(
        latency_ms=0
    )


@pytest.fixture
def limiter_factory(redis_client):

    def create_limiter(
        request_limit: int
    ):

        return SlidingWindowCounter(

            redis_client=redis_client,

            request_limit=request_limit,

            window_size_seconds=TEST_WINDOW_SIZE
        )

    return create_limiter


@pytest.mark.asyncio
async def test_should_allow_requests_until_limit(
    limiter_factory
):

    rate_limiter = limiter_factory(
        request_limit=2
    )

    first_request = await rate_limiter.is_allowed(
        "client_1"
    )

    second_request = await rate_limiter.is_allowed(
        "client_1"
    )

    third_request = await rate_limiter.is_allowed(
        "client_1"
    )

    assert first_request["allowed"] is True
    assert second_request["allowed"] is True
    assert third_request["allowed"] is False


@pytest.mark.asyncio
async def test_should_handle_window_boundary_precision(
    limiter_factory
):

    rate_limiter = limiter_factory(
        request_limit=2
    )

    await rate_limiter.is_allowed(

        client_id="user_1",

        current_time=0.0
    )

    await rate_limiter.is_allowed(

        client_id="user_1",

        current_time=0.9
    )

    boundary_request = await rate_limiter.is_allowed(

        client_id="user_1",

        current_time=1.1
    )

    assert boundary_request["allowed"] is False


@pytest.mark.asyncio
async def test_should_return_retry_after_when_throttled(
    limiter_factory
):

    rate_limiter = limiter_factory(
        request_limit=1
    )

    await rate_limiter.is_allowed(
        "client_retry"
    )

    throttled_response = await rate_limiter.is_allowed(
        "client_retry"
    )

    assert throttled_response["allowed"] is False
    assert throttled_response["retry_after"] > 0


@pytest.mark.asyncio
async def test_should_isolate_multiple_clients(
    limiter_factory
):

    rate_limiter = limiter_factory(
        request_limit=1
    )

    first_client = await rate_limiter.is_allowed(
        "tenant_a"
    )

    second_client = await rate_limiter.is_allowed(
        "tenant_b"
    )

    assert first_client["allowed"] is True
    assert second_client["allowed"] is True
    