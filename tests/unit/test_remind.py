from http import HTTPStatus

from app.db.fitness_classes import FitnessClassResource
from tests.utils import auth_header, sample_class_data, past_date_str

def _create_class_with_booking(client, admin_token, member_token):
    resp = client.post("/classes/", json=sample_class_data(),
                       headers=auth_header(admin_token))
    class_id = resp.get_json()["message"].split("id: ")[1]
    client.post(f"/classes/{class_id}/book",
                headers=auth_header(member_token))
    return class_id

def test_remind_success_trainer(client, admin_token, member_token,
                                trainer_token, mock_email_service):
    class_id = _create_class_with_booking(client, admin_token, member_token)

    resp = client.post(f"/classes/{class_id}/remind",
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.OK
    assert "1 participants" in resp.get_json()["message"]
    mock_email_service.send_reminder.assert_called_once()

def test_remind_success_admin(client, admin_token, member_token,
                              mock_email_service):
    class_id = _create_class_with_booking(client, admin_token, member_token)

    resp = client.post(f"/classes/{class_id}/remind",
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.OK

def test_remind_forbidden_member(client, member_token, admin_token,
                                 created_class_id, mock_email_service):
    resp = client.post(f"/classes/{created_class_id}/remind",
                       headers=auth_header(member_token))
    assert resp.status_code == HTTPStatus.FORBIDDEN

def test_remind_no_auth(client, created_class_id):
    resp = client.post(f"/classes/{created_class_id}/remind")
    assert resp.status_code in (HTTPStatus.UNAUTHORIZED,
                                HTTPStatus.INTERNAL_SERVER_ERROR)

def test_remind_class_not_found(client, trainer_token, mock_email_service):
    resp = client.post("/classes/000000000000000000000000/remind",
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.NOT_FOUND

def test_remind_invalid_class_id(client, trainer_token, mock_email_service):
    resp = client.post("/classes/bad-id/remind",
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.NOT_FOUND

def test_remind_no_participants(client, admin_token, created_class_id,
                                mock_email_service):
    resp = client.post(f"/classes/{created_class_id}/remind",
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "No participants" in resp.get_json()["message"]

def test_remind_class_already_started(client, trainer_token, mock_email_service):
    fc = FitnessClassResource()
    class_id = fc.create_fitness_class(
        "Old Yoga", "desc", past_date_str(), "10:00", "11:00",
        "Gym", "Jane", 10, "admin@test.com",
    )
    fc.book_class(class_id, {"name": "A", "email": "a@test.com", "phone": "1"})

    resp = client.post(f"/classes/{class_id}/remind",
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "already started" in resp.get_json()["message"]

def test_remind_email_service_failure(client, admin_token, member_token,
                                      mock_email_service):
    mock_email_service.send_reminder.side_effect = Exception("SES down")
    class_id = _create_class_with_booking(client, admin_token, member_token)

    resp = client.post(f"/classes/{class_id}/remind",
                       headers=auth_header(admin_token))
    assert resp.status_code == HTTPStatus.OK
    assert "0 participants" in resp.get_json()["message"]


def test_remind_telegram_channel(client, admin_token, member_token,
                                 trainer_token, mock_email_service,
                                 mock_telegram_requests):
    client.put("/auth/preferences", json={
        "notification_channels": ["telegram"],
        "telegram_chat_id": "123456789",
    }, headers=auth_header(member_token))

    class_id = _create_class_with_booking(client, admin_token, member_token)

    resp = client.post(f"/classes/{class_id}/remind",
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.OK
    assert "1 participants" in resp.get_json()["message"]
    mock_telegram_requests.assert_called_once()


def test_remind_both_channels(client, admin_token, member_token,
                              trainer_token, mock_email_service,
                              mock_telegram_requests):
    client.put("/auth/preferences", json={
        "notification_channels": ["email", "telegram"],
        "telegram_chat_id": "987654321",
    }, headers=auth_header(member_token))

    class_id = _create_class_with_booking(client, admin_token, member_token)

    resp = client.post(f"/classes/{class_id}/remind",
                       headers=auth_header(trainer_token))
    assert resp.status_code == HTTPStatus.OK
    assert "1 participants" in resp.get_json()["message"]
    mock_email_service.send_reminder.assert_called_once()
    mock_telegram_requests.assert_called_once()
