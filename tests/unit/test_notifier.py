from unittest.mock import MagicMock, patch
from app.services.notifier import EmailNotifier, TelegramNotifier

def test_email_notifier_calls_send_reminder():
   mock_svc = MagicMock()
   notifier = EmailNotifier(mock_svc)
   recipient = {"email": "a@test.com", "name": "A", "phone": "1"}
   fitness_class = {"name": "Yoga", "date": "2026-05-01", "start_time": "10:00", "location": "Gym"}
   notifier.send_reminder(recipient, fitness_class)
   mock_svc.send_reminder.assert_called_once_with(
       to_email="a@test.com",
       class_name="Yoga",
       date="2026-05-01",
       start_time="10:00",
       location="Gym",
   )

def test_email_notifier_missing_fields_defaults_to_empty():
   mock_svc = MagicMock()
   notifier = EmailNotifier(mock_svc)
   notifier.send_reminder({}, {})
   mock_svc.send_reminder.assert_called_once_with(
       to_email="", class_name="", date="", start_time="", location="",
   )

def test_telegram_notifier_sends_message():
   with patch("app.services.notifier.requests.post") as mock_post:
       notifier = TelegramNotifier("test-token")
       recipient = {"email": "a@test.com", "telegram_chat_id": "123456"}
       fitness_class = {"name": "Yoga", "date": "2026-05-01", "start_time": "10:00", "location": "Gym"}
       notifier.send_reminder(recipient, fitness_class)
       mock_post.assert_called_once()
       call_kwargs = mock_post.call_args[1]
       assert call_kwargs["json"]["chat_id"] == "123456"
       assert "Yoga" in call_kwargs["json"]["text"]
       assert "2026-05-01" in call_kwargs["json"]["text"]

def test_telegram_notifier_skips_when_no_chat_id():
   with patch("app.services.notifier.requests.post") as mock_post:
       notifier = TelegramNotifier("test-token")
       recipient = {"email": "a@test.com", "telegram_chat_id": ""}
       fitness_class = {"name": "Yoga", "date": "2026-05-01", "start_time": "10:00", "location": "Gym"}
       notifier.send_reminder(recipient, fitness_class)
       mock_post.assert_not_called()

def test_telegram_notifier_skips_when_chat_id_missing():
   with patch("app.services.notifier.requests.post") as mock_post:
       notifier = TelegramNotifier("test-token")
       notifier.send_reminder({}, {"name": "Yoga"})
       mock_post.assert_not_called()

def test_telegram_notifier_uses_custom_base_url():
   with patch("app.services.notifier.requests.post") as mock_post:
       notifier = TelegramNotifier("mytoken", base_url="http://mock-telegram")
       recipient = {"telegram_chat_id": "999"}
       fitness_class = {"name": "Yoga", "date": "2026-05-01", "start_time": "10:00", "location": "Gym"}
       notifier.send_reminder(recipient, fitness_class)
       call_url = mock_post.call_args[0][0]
       assert call_url.startswith("http://mock-telegram")
       assert "mytoken" in call_url

def test_telegram_notifier_message_contains_location():
   with patch("app.services.notifier.requests.post") as mock_post:
       notifier = TelegramNotifier("test-token")
       recipient = {"telegram_chat_id": "111"}
       fitness_class = {"name": "Pilates", "date": "2026-06-01", "start_time": "09:00", "location": "Studio A"}
       notifier.send_reminder(recipient, fitness_class)
       text = mock_post.call_args[1]["json"]["text"]
       assert "Studio A" in text
