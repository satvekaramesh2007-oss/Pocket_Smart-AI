def get_auth_headers(client):
    reg = client.post("/register", json={
        "name": "Rec Tester",
        "email": "rec@example.com",
        "password": "password123",
        "confirm_password": "password123"
    })
    token = reg.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_recommendation_lifecycle(client):
    headers = get_auth_headers(client)

    # 1. Create a Home plan
    home_res = client.post("/generate-home", json={
        "budget": 60000,
        "home_type": "Apartment",
        "room_type": "Bedroom",
        "style": "Minimalist"
    }, headers=headers)
    assert home_res.status_code == 201
    rec_id = home_res.json()["id"]

    # 2. Retrieve recommendation details
    detail_res = client.get(f"/recommendations/{rec_id}", headers=headers)
    assert detail_res.status_code == 200
    assert detail_res.json()["id"] == rec_id

    # 3. Toggle Save Item
    save_res = client.post(f"/recommendations/{rec_id}/save", headers=headers)
    assert save_res.status_code == 200
    assert save_res.json()["is_saved"] is True

    # 4. Fetch History
    hist_res = client.get("/api/history", headers=headers)
    assert hist_res.status_code == 200
    assert len(hist_res.json()["history"]) == 1
    assert hist_res.json()["history"][0]["is_saved"] is True

    # 5. Delete Recommendation
    del_res = client.delete(f"/recommendations/{rec_id}", headers=headers)
    assert del_res.status_code == 200

    # 6. Verify Deleted
    hist_res_after = client.get("/api/history", headers=headers)
    assert len(hist_res_after.json()["history"]) == 0
