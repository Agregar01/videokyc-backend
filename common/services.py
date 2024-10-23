import json
import requests
from config import settings
from django.core.mail import send_mail
from background_task import background
from config import settings

class CommonSerivces:

    @background(schedule=1)
    def email_notification(subject, message, email):
        from_email = settings.EMAIL_HOST_FROM
        send_mail(subject, message, from_email, [email])


    # @background(schedule=1)
    def send_callback(message: dict, url: str):
        message = json.dumps(message)
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.request("POST", url=url, headers=headers, data=message)
        return response
