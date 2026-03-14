from http import HTTPStatus


def test_get_all_classes_returns_ok(client):
    """GET /classes/ is public — should return 200 with a message key."""
    response = client.get("/classes/")
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert "message" in data
    assert isinstance(data["message"], list)


def test_get_all_classes_empty(client):
    response = client.get("/classes/")
    assert response.get_json()["message"] == []


def test_get_all_classes_with_data(client, admin_token):
    client.post("/classes/", json=sample_class_data(name="Yoga"),
                headers=auth_header(admin_token))
    client.post("/classes/", json=sample_class_data(name="Pilates"),
                headers=auth_header(admin_token))
    response = client.get("/classes/")
    classes = response.get_json()["message"]
    assert len(classes) == 2
    names = {c["name"] for c in classes}
    assert names == {"Yoga", "Pilates"}
