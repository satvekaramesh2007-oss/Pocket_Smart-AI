import io
import pytest

def get_auth_headers(client):
    reg = client.post("/register", json={
        "name": "Planner Tester",
        "email": "planner@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_home_planner_endpoint(client):
    headers = get_auth_headers(client)
    payload = {
        "budget": 50000,
        "home_type": "Apartment",
        "room_type": "Living Room",
        "style": "Modern",
        "items_required": ["Sofa", "Lights"],
        "color_preference": "Beige"
    }
    response = client.post("/generate-home", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["planner_type"] == "home"

def test_party_planner_endpoint(client):
    headers = get_auth_headers(client)
    payload = {
        "budget": 100000,
        "guests": 50,
        "event_type": "Birthday",
        "venue_preference": "Banquet Hall",
        "accommodation_required": False
    }
    response = client.post("/generate-party", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["planner_type"] == "party"

def test_jewelry_planner_endpoint_with_image(client):
    headers = get_auth_headers(client)
    
    # Create dummy image file in memory
    dummy_image = io.BytesIO(b"fake image bytes content")
    
    data = {
        "budget": "5000",
        "occasion": "Wedding",
        "jewelry_type": "Necklace",
        "style": "Traditional",
        "metal_preference": "Gold Plated",
        "outfit_color": "Royal Blue"
    }
    files = {
        "outfit_image": ("outfit.jpg", dummy_image, "image/jpeg")
    }

    response = client.post("/generate-jewelry", data=data, files=files, headers=headers)
    assert response.status_code == 201
    res = response.json()
    assert "id" in res
    assert res["planner_type"] == "jewelry"
