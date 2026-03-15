import os
import boto3
from app.config import Config


class EmailService:
    def __init__(self, ses_client=None, sender=None):
        self.region = Config.AWS_SES_REGION
        self.sender = sender or os.environ.get("SES_SENDER_EMAIL", "")
        if ses_client is not None:
            self.client = ses_client
        else:
            self.client = boto3.client("ses", region_name=self.region)

    def send_reminder(self, to_email, class_name, date, start_time, location):
        subject = f"Reminder: {class_name} on {date}"
        body = (
            f"This is a reminder for your upcoming fitness class:\n\n"
            f"Class: {class_name}\n"
            f"Date: {date}\n"
            f"Time: {start_time}\n"
            f"Location: {location}\n\n"
            f"See you there!"
        )
        self.client.send_email(
            Source=self.sender,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )

    def send_class_reminders(self, fitness_class):
        participants = fitness_class.get("participants", [])
        sent = 0
        for p in participants:
            email = p.get("email") if isinstance(p, dict) else p
            if not email:
                continue
            try:
                self.send_reminder(
                    to_email=email,
                    class_name=fitness_class.get("name", ""),
                    date=fitness_class.get("date", ""),
                    start_time=fitness_class.get("start_time", ""),
                    location=fitness_class.get("location", ""),
                )
                sent += 1
            except Exception:
                continue
        return sent
