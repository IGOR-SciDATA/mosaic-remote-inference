def test_inference_requires_token(client):
    response = client.post("/v1/inference", json={"messages": [{"role": "user", "content": "Oi"}]})
    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}


def test_inference_rejects_wrong_token(client):
    response = client.post("/v1/inference", headers={"Authorization": "Bearer wrong"}, json={"messages": [{"role": "user", "content": "Oi"}]})
    assert response.status_code == 401


def test_inference_accepts_valid_token(client):
    response = client.post("/v1/inference", headers={"Authorization": "Bearer test-secret-token"}, json={"messages": [{"role": "user", "content": "Oi"}]})
    assert response.status_code == 200
    assert response.json()["output_text"] == "Resposta de teste"
