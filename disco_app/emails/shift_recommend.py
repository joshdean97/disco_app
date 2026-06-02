import resend
from django.conf import settings


def send_shift_recommendation_email(staff, shift):
    if not staff.user.email:
        return

    subject = f"New shift available: {shift.role_required}"

    html = f"""
    <h2>New shift recommended for you</h2>

    <p>Hi {staff.user.first_name or staff.user.username},</p>

    <p>A shift matching your profile has just been posted on Disco.</p>

    <p>
        <strong>Role:</strong> {shift.role_required}<br>
        <strong>Venue:</strong> {shift.site.name}<br>
        <strong>Date:</strong> {shift.date}<br>
        <strong>Time:</strong> {shift.start_time} - {shift.end_time}<br>
        <strong>Pay:</strong> £{shift.hourly_rate}/hour
    </p>

    <p>
        <a href="https://discoapp.co.uk/shifts/">
            View and apply for this shift
        </a>
    </p>

    <p>Disco</p>
    """

    resend.Emails.send(
        {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [staff.user.email],
            "subject": subject,
            "html": html,
        }
    )
