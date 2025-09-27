import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_signup_and_login():
    username = f"test_{uuid.uuid4().hex[:8]}"
    password = "pass123"

    # Signup
    r = client.post(
        "/signup",
        json={"username": username, "password": password}  # JSON, inte data
    )
    assert r.status_code == 200

    # Login
    r = client.post(
        "/login",
        json={"username": username, "password": password}  # JSON även här
    )
    assert r.status_code == 200

    data = r.json()
    assert isinstance(data, dict)
