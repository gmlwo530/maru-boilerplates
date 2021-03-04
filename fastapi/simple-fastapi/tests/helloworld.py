from fastapi.testclient import TestClient


def test_hello_world(client: TestClient) -> None:
    r = client.get("/")
    assert r.status_code == 200
