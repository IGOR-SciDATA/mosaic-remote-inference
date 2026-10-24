def auth():
    return {"Authorization": "Bearer test-secret-token"}


def test_rejects_extra_request_fields(client):
    response = client.post("/v1/inference", headers=auth(), json={"messages": [{"role": "user", "content": "Oi"}], "api_key": "secret"})
    assert response.status_code == 422
    assert "secret" not in response.text


def test_rejects_invalid_role(client):
    response = client.post("/v1/inference", headers=auth(), json={"messages": [{"role": "tool", "content": "Oi"}]})
    assert response.status_code == 422


def test_enforces_configured_input_limit(client):
    response = client.post("/v1/inference", headers=auth(), json={"messages": [{"role": "user", "content": "x" * 101}]})
    assert response.status_code == 413
    assert response.json()["detail"] == "Request exceeds configured input limit"


def test_inference_does_not_return_secrets(client):
    response = client.post("/v1/inference", headers=auth(), json={"messages": [{"role": "user", "content": "Olá"}]})
    assert response.status_code == 200
    assert "test-secret-token" not in response.text


def test_stream_requires_auth(client):
    response = client.post("/v1/inference/stream", json={"messages": [{"role": "user", "content": "Oi"}]})
    assert response.status_code == 401


def test_stream_returns_incremental_sse_and_terminal_marker(client):
    with client.stream("POST", "/v1/inference/stream", headers=auth(), json={"messages": [{"role": "user", "content": "Oi"}]}) as response:
        body = "".join(response.iter_text())
    assert response.status_code == 200
    assert '"text":"Resposta "' in body
    assert '"text":"em "' in body
    assert '"text":"streaming"' in body
    assert "data: [DONE]" in body


def test_capabilities_advertise_streaming(client):
    response = client.get("/v1/capabilities")
    assert response.status_code == 200
    assert response.json()["streaming"] is True
