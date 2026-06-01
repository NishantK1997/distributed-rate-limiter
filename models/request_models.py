from pydantic import BaseModel


class RateLimitRequest(
    BaseModel
):

    node_id: str

    tenant_id: str

    client_id: str
