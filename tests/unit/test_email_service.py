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


