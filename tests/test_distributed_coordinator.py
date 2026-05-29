import pytest

from algorithms.distributed_coordinator import (
    DistributedRateLimiter
)

from storage.redis_simulator import (
    RedisSimulator
)


@pytest.fixture
def coordinator():

    redis_client = RedisSimulator(
        latency_ms=0
    )

    instance = DistributedRateLimiter(

        redis_client=redis_client,

        request_limit=2,

        window_size_seconds=1
    )

    instance.register_node(
        "node_a"
    )

    instance.register_node(
        "node_b"
    )

    instance.register_node(
        "node_c"
    )

    return instance


@pytest.mark.asyncio
async def test_should_enforce_global_limit(
    coordinator
):

    first = await coordinator.allow_request(
        "node_a",
        "client_x"
    )

    second = await coordinator.allow_request(
        "node_b",
        "client_x"
    )

    third = await coordinator.allow_request(
        "node_c",
        "client_x"
    )

    assert first["allowed"] is True

    assert second["allowed"] is True

    assert third["allowed"] is False


def test_should_reject_duplicate_node():

    redis_client = RedisSimulator(
        latency_ms=0
    )

    coordinator = DistributedRateLimiter(

        redis_client=redis_client,

        request_limit=5,

        window_size_seconds=1
    )

    coordinator.register_node(
        "node_a"
    )

    with pytest.raises(
        ValueError
    ):

        coordinator.register_node(
            "node_a"
        )


@pytest.mark.asyncio
async def test_should_reject_unknown_node(
    coordinator
):

    with pytest.raises(
        ValueError
    ):

        await coordinator.allow_request(

            "missing_node",

            "client"
        )


def test_should_track_registered_nodes():

    redis_client = RedisSimulator(
        latency_ms=0
    )

    coordinator = DistributedRateLimiter(

        redis_client=redis_client,

        request_limit=10,

        window_size_seconds=1
    )

    coordinator.register_node(
        "node_1"
    )

    coordinator.register_node(
        "node_2"
    )

    assert (

        coordinator
        .registered_nodes_count()

        == 2
    )