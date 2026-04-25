from unittest.mock import MagicMock

from app.services.email_service import EmailService

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

def test_send_reminder_subject_contains_date():
    mock_client = MagicMock()
    service = EmailService(ses_client=mock_client, sender="gym@example.com")
    service.send_reminder("user@test.com", "Pilates", "2026-05-10", "09:00", "Studio")
    call_kwargs = mock_client.send_email.call_args[1]
    assert "2026-05-10" in call_kwargs["Message"]["Subject"]["Data"]
