def test_user_registration_success(client):
    payload = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"

def test_user_registration_password_mismatch(client):
    payload = {
        "name": "Test User",
        "email": "test2@example.com",
        "password": "password123",
        "confirm_password": "mismatch_password"
    }
    response = client.post("/register", json=payload)
    assert response.status_code == 422  # Validation Error

def test_user_registration_duplicate_email(client):
    payload = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    client.post("/register", json=payload)
    
    # Try registering again with duplicate email
    response = client.post("/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_user_login_success(client):
    # Register user first
    client.post("/register", json={
        "name": "Login User",
        "email": "login@example.com",
        "password": "secretpassword",
        "confirm_password": "secretpassword"
    })

    # Login
    response = client.post("/login", json={
        "email": "login@example.com",
        "password": "secretpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_user_login_invalid_credentials(client):
    response = client.post("/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
