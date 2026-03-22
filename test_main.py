from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_ask_without_token():
    response = client.post("/api/v1/ask", json={"question": "What is a root canal?"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_login_success():
    response = client.post(
        "/api/v1/login",
        data={"username": "admin", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_failure():
    response = client.post(
        "/api/v1/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
