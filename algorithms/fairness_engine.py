from typing import Any, Dict, Optional

from algorithms.token_bucket import (
    TokenBucket
)


class TenantFairnessEngine:

    def __init__(self) -> None:

        self.tenant_buckets: Dict[
            str,
            TokenBucket
        ] = {}

    def register_tenant(
        self,
        tenant_id: str,
        requests_per_second: int,
        burst_capacity: int
    ) -> None:

        normalized_tenant_id = (
            tenant_id.strip()
        )

        if not normalized_tenant_id:

            raise ValueError(
                "tenant_id cannot be empty"
            )

        self.tenant_buckets[
            normalized_tenant_id
        ] = TokenBucket(

            refill_rate_per_second=(
                requests_per_second
            ),

            max_bucket_capacity=(
                burst_capacity
            )
        )

    def is_request_allowed(
        self,
        tenant_id: str
    ) -> bool:

        tenant_bucket = (

            self.tenant_buckets.get(
                tenant_id
            )
        )

        if tenant_bucket is None:

            return False

        return (
            tenant_bucket
            .consume_tokens()
        )

    def get_tenant_state(
        self,
        tenant_id: str
    ) -> Optional[
        Dict[str, Any]
    ]:

        tenant_bucket = (

            self.tenant_buckets.get(
                tenant_id
            )
        )

        if tenant_bucket is None:

            return None

        return (
            tenant_bucket
            .get_bucket_state()
        )