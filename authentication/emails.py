import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY


def send_welcome_email(user):
    if not user.email:
        return

    resend.Emails.send(
        {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [user.email],
            "subject": "Welcome to Disco 🪩",
            "html": f"""
        <h1>Welcome to Disco 🪩</h1>
        <p>Hi {user.first_name or user.username},</p>
        <p>Thanks for joining Disco.</p>
        <p>You're one of the first hospitality people helping us build something better.</p>
        <p>Log in, complete your profile, and start finding shifts.</p>
        <p>— Josh & Team Disco</p>
        """,
        }
    )
