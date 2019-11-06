from requests import post


class MailgunException(Exception):
    def __init_(self, message):
        super().__init__(message)


class Mailgun:

    MAILGUN_DOMAIN = "sandboxe43757f5d97049139699ab8c84c7eca6.mailgun.org"
    MAILGUN_API_KEY = "3d8433b5ba8f1622374c12c70eccfd79-f696beb4-ab0c0c60"
    FROM_EMAIL = "postmaster@sandboxe43757f5d97049139699ab8c84c7eca6.mailgun.org"
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