def test_liveness_is_independent_of_runtime(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_readiness_reports_runtime(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "runtime_available": True}


def test_capabilities_are_explicit(client):
    data = client.get("/v1/capabilities").json()
    assert data["streaming"] is False
    assert data["tools"] is False
    assert data["configured_model"] == "test-model"
