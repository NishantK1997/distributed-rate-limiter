import time

from typing import Any, Dict

from config.constants import (
    DEFAULT_TOKEN_COST
)


class TokenBucket:

    def __init__(
        self,
        refill_rate_per_second: int,
        max_bucket_capacity: int
    ):

        if refill_rate_per_second <= 0:
            raise ValueError(
                "refill_rate_per_second must be positive"
            )

        if max_bucket_capacity <= 0:
            raise ValueError(
                "max_bucket_capacity must be positive"
            )

        self.refill_rate_per_second = (
            refill_rate_per_second
        )

        self.max_bucket_capacity = (
            max_bucket_capacity
        )

        self.available_tokens = float(
            max_bucket_capacity
        )

        self.last_refill_timestamp = (
            time.time()
        )

    def _refill_bucket(
        self
    ):

        current_timestamp = (
            time.time()
        )

        elapsed_seconds = max(

            0,

            current_timestamp -

            self.last_refill_timestamp
        )

        generated_tokens = (

            elapsed_seconds *

            self.refill_rate_per_second
        )

        self.available_tokens = min(

            self.max_bucket_capacity,

            self.available_tokens +

            generated_tokens
        )

        self.last_refill_timestamp = (
            current_timestamp
        )

    def consume_tokens(
        self,
        token_count: int = (
            DEFAULT_TOKEN_COST
        )
    ):

        if token_count <= 0:
            raise ValueError(
                "token_count must be positive"
            )

        self._refill_bucket()

        if self.available_tokens < token_count:

            return False

        self.available_tokens -= (
            token_count
        )

        return True

    def get_bucket_state(
        self
    ):

        return {

            "available_tokens": round(
                self.available_tokens,
                2
            ),

            "max_capacity": (
                self.max_bucket_capacity
            ),

            "refill_rate_per_second": (
                self.refill_rate_per_second
            )
        }