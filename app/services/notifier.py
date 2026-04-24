from abc import ABC, abstractmethod
import requests

TELEGRAM_BASE_URL = "https://api.telegram.org"

class BaseNotifier(ABC):
   @abstractmethod
   def send_reminder(self, recipient: dict, fitness_class: dict) -> None:
       pass

class EmailNotifier(BaseNotifier):
   def __init__(self, email_service):
       self._service = email_service


   def send_reminder(self, recipient: dict, fitness_class: dict) -> None:
       self._service.send_reminder(
           to_email=recipient.get("email", ""),
           class_name=fitness_class.get("name", ""),
           date=fitness_class.get("date", ""),
           start_time=fitness_class.get("start_time", ""),
           location=fitness_class.get("location", ""),
       )

class TelegramNotifier(BaseNotifier):
   def __init__(self, bot_token: str, base_url: str = TELEGRAM_BASE_URL):
       self._token = bot_token
       self._base_url = base_url


   def send_reminder(self, recipient: dict, fitness_class: dict) -> None:
       chat_id = recipient.get("telegram_chat_id", "")
       if not chat_id:
           return
       text = (
           f"Reminder: {fitness_class.get('name', '')} on "
           f"{fitness_class.get('date', '')} at "
           f"{fitness_class.get('start_time', '')} "
           f"@ {fitness_class.get('location', '')}"
       )
       url = f"{self._base_url}/bot{self._token}/sendMessage"
       requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)