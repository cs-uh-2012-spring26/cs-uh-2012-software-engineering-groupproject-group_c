from http import HTTPStatus


def test_get_all_classes_returns_ok(client):
    """GET /classes/ is public — should return 200 with a message key."""
    response = client.get("/classes/")
    assert response.status_code == HTTPStatus.OK
    data = response.get_json()
    assert "message" in data
    assert isinstance(data["message"], list)
