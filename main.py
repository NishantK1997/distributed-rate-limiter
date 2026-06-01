from fastapi import FastAPI

from models.request_models import (
    RateLimitRequest
)

from services.rate_limiter_service import (
    RateLimiterService
)


app = FastAPI(
    title="Distributed Rate Limiter",
    version="1.0.0"
)


rate_limiter_service = (
    RateLimiterService(
        request_limit=100,
        window_size_seconds=1
    )
)


rate_limiter_service.distributed_limiter.register_node(
    "node_1"
)

rate_limiter_service.fairness_engine.register_tenant(
    tenant_id="default",
    requests_per_second=100,
    burst_capacity=100
)


@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }


@app.post("/rate-limit")
async def check_rate_limit(
    request: RateLimitRequest
):

    return await (
        rate_limiter_service
        .allow_request(
            node_id=request.node_id,
            tenant_id=request.tenant_id,
            client_id=request.client_id
        )
    )
