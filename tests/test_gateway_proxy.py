from fastapi.testclient import TestClient
from gateway.main import app as gateway_app


client = TestClient(gateway_app)


def test_gateway_404():  # noqa: D401
    assert client.get("/no-service/foo").status_code == 404