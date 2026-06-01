from fastapi.testclient import (
    TestClient
)

from main import app


client = TestClient(
    app
)


def test_should_allow_request():

    response = client.post(

        "/rate-limit",

        json={

            "node_id": "node_1",

            "tenant_id": "default",

            "client_id": "client_1"
        }
    )

    assert response.status_code == 200

    assert (

        response.json()["allowed"]

        is True
    )


def test_health_endpoint():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {

        "status": "healthy"
    }
    