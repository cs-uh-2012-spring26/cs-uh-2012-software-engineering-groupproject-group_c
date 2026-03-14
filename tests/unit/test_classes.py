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

def test_get_all_classes_excludes_participants(client, admin_token):
    client.post("/classes/", json=sample_class_data(),
                headers=auth_header(admin_token))
    response = client.get("/classes/")
    classes = response.get_json()["message"]
    for c in classes:
        assert "participants" not in c


def test_create_class_success(client, admin_token):
    resp = client.post("/classes/", json=sample_class_data(),
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.CREATED
    assert "created with id" in resp.get_json()["message"]


def test_create_class_forbidden_member(client, member_token):
    resp = client.post("/classes/", json=sample_class_data(),
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_create_class_forbidden_trainer(client, trainer_token):
    resp = client.post("/classes/", json=sample_class_data(),
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.FORBIDDEN


def test_create_class_no_auth(client):
    resp = client.post("/classes/", json=sample_class_data())
    assert resp.status_code in (HTTPStatus.UNAUTHORIZED,
                                HTTPStatus.INTERNAL_SERVER_ERROR)


def test_create_class_missing_fields(client, admin_token):
    resp = client.post("/classes/", json={"name": "Yoga"},
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_class_invalid_capacity_negative(client, admin_token):
    resp = client.post("/classes/", json=sample_class_data(capacity=-1),
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_class_past_date(client, admin_token):
    resp = client.post("/classes/", json=sample_class_data(date=past_date_str()),
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST


def test_create_class_invalid_date_format(client, admin_token):
    resp = client.post("/classes/", json=sample_class_data(date="not-a-date"),
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST

