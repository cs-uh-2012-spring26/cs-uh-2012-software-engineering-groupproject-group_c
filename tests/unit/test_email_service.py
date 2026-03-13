from unittest.mock import MagicMock

from app.services.email_service import EmailService
import app.services.email_service as email_module


def test_send_reminder_calls_ses():
    mock_client = MagicMock()
    service = EmailService(ses_client=mock_client, sender="gym@example.com")
    service.send_reminder("user@test.com", "Yoga", "2026-04-01", "10:00", "Gym")

    mock_client.send_email.assert_called_once()
    call_kwargs = mock_client.send_email.call_args[1]
    assert call_kwargs["Destination"]["ToAddresses"] == ["user@test.com"]
    assert call_kwargs["Source"] == "gym@example.com"
    assert "Yoga" in call_kwargs["Message"]["Subject"]["Data"]
    assert "Gym" in call_kwargs["Message"]["Body"]["Text"]["Data"]

def test_send_class_reminders_multiple_participants():
    mock_client = MagicMock()
    service = EmailService(ses_client=mock_client, sender="gym@example.com")
    fitness_class = {
        "name": "Yoga",
        "date": "2026-04-01",
        "start_time": "10:00",
        "location": "Gym",
        "participants": [
            {"name": "A", "email": "a@test.com", "phone": "123"},
            {"name": "B", "email": "b@test.com", "phone": "456"},
        ],
    }
    count = service.send_class_reminders(fitness_class)
    assert count == 2
    assert mock_client.send_email.call_count == 2

def test_send_class_reminders_empty():
    mock_client = MagicMock()
    service = EmailService(ses_client=mock_client, sender="gym@example.com")
    count = service.send_class_reminders({"participants": []})
    assert count == 0
    mock_client.send_email.assert_not_called()


def test_send_class_reminders_partial_failure():
    mock_client = MagicMock()
    mock_client.send_email.side_effect = [None, Exception("SES error"), None]
    service = EmailService(ses_client=mock_client, sender="gym@example.com")
    fitness_class = {
        "name": "Yoga", "date": "2026-04-01",
        "start_time": "10:00", "location": "Gym",
        "participants": [
            {"name": "A", "email": "a@test.com", "phone": "1"},
            {"name": "B", "email": "b@test.com", "phone": "2"},
            {"name": "C", "email": "c@test.com", "phone": "3"},
        ],
    }
    count = service.send_class_reminders(fitness_class)
    assert count == 2  


