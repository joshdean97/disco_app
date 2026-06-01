import resend
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY


def send_welcome_email(user):
    if not user.email:
        return

    name = user.first_name or user.username

    resend.Emails.send(
        {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [user.email],
            "subject": "Welcome to Disco 🪩",
            "html": f"""
        <div style="
            font-family: Arial, sans-serif;
            background-color: #f4f7fb;
            padding: 32px;
        ">
            <div style="
                max-width: 560px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 18px;
                padding: 32px;
                border: 1px solid #e5e7eb;
            ">
                <h1 style="
                    color: #101828;
                    font-size: 32px;
                    margin-bottom: 16px;
                ">
                    Welcome to Disco 🪩
                </h1>

                <p style="font-size: 16px; color: #344054;">
                    Hi {name},
                </p>

                <p style="font-size: 16px; color: #344054; line-height: 1.6;">
                    Thanks for joining Disco. You're one of the first hospitality people helping us build something better.
                </p>

                <p style="font-size: 16px; color: #344054; line-height: 1.6;">
                    Log in, complete your profile, and start finding shifts.
                </p>

                <a href="https://discoapp.co.uk/login/"
                   style="
                    display: inline-block;
                    background: #00d4ff;
                    color: #000000;
                    padding: 14px 24px;
                    border-radius: 999px;
                    text-decoration: none;
                    font-weight: bold;
                    margin: 20px 0;
                   ">
                    Log in to Disco
                </a>

                <p style="font-size: 14px; color: #667085; line-height: 1.6;">
                    We're still early, so your feedback genuinely helps shape what Disco becomes.
                </p>

                <p style="font-size: 16px; color: #344054;">
                    — Josh & Team Disco
                </p>
            </div>
        </div>
        """,
        }
    )
