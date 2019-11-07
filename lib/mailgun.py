import os
from requests import post


class MailgunException(Exception):
    def __init_(self, message):
        super().__init__(message)


class Mailgun:

    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN")
    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY")
    FROM_EMAIL = os.getenv("FROM_EMAIL")
    FROM_TITLE = "Store Rest API"

    @classmethod
    def send_email(cls, email, subject, text=None, html=None):
        response = post(
            f"http://api.mailgun.net/v3/{cls.MAILGUN_DOMAIN}/messages",
            auth=("api", cls.MAILGUN_API_KEY),
            data={
                "from": f"{cls.FROM_TITLE} <{cls.FROM_EMAIL}>",
                "to": email,
                "subject": subject,
                "text": text,
                "html": html
            }
        )

        if response.status_code != 200:
            raise MailgunException('Error in sending confirmation email')

        return response