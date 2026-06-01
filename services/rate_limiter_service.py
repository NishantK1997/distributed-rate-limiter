from algorithms.distributed_coordinator import (
    DistributedRateLimiter
)

from algorithms.fairness_engine import (
    TenantFairnessEngine
)

from algorithms.priority_queue import (
    PriorityScheduler
)

from storage.redis_simulator import (
    RedisSimulator
)


class RateLimiterService:

    def __init__(
        self,
        request_limit: int,
        window_size_seconds: int
    ):

        redis_client = RedisSimulator(
            latency_ms=50
        )

        self.distributed_limiter = (
            DistributedRateLimiter(

                redis_client=redis_client,

                request_limit=request_limit,

                window_size_seconds=(
                    window_size_seconds
                )
            )
        )

        self.fairness_engine = (
            TenantFairnessEngine()
        )

        self.priority_scheduler = (
            PriorityScheduler()
        )

    async def allow_request(
        self,
        node_id: str,
        tenant_id: str,
        client_id: str
    ):

        tenant_allowed = (

            self.fairness_engine
            .is_request_allowed(
                tenant_id
            )
        )

        if not tenant_allowed:

            return {

                "allowed": False,

                "reason": "tenant_limit",

                "retry_after": 0
            }

        return await (

            self.distributed_limiter
            .allow_request(

                node_id,

                client_id
            )
        )
        