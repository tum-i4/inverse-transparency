""" Unit tests creating a local mock Overseer client. """

from fastapi.testclient import TestClient

from overseer.main import overseer

overseer_client = TestClient(overseer)


def test_health():
    """test overseer running and database connected"""
    response = overseer_client.get("/health")
    assert response.status_code == 200


def test_docs_load():
    """test overseer api docs presented"""
    response = overseer_client.get("/docs")
    assert "text/html" in response.headers["content-type"]
    assert response.status_code == 200
