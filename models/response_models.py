from pydantic import BaseModel


class RateLimitResponse(
    BaseModel
):

    allowed: bool

    retry_after: float = 0

    reason: str | None = None
