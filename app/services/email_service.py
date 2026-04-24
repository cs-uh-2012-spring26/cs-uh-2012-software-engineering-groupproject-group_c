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
