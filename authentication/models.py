from django.db import models
from django.contrib.auth.models import User


class Staff(models.Model):
    ROLE_CHOICES = [
        ("chef", "Chef"),
        ("bartender", "Bartender"),
        ("waiting_staff", "Waiting Staff"),
        ("barista", "Barista"),
        ("not_set", "Not Set"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    primary_role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default="not_set",
    )
    year_started = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True)
    travel_radius_miles = models.PositiveIntegerField(default=5)
    postcode = models.CharField(max_length=20, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    disco_rank = models.PositiveIntegerField(default=70)
    completed_shifts = models.PositiveIntegerField(default=0)
    cancelled_shifts = models.PositiveIntegerField(default=0)
    no_shows = models.PositiveIntegerField(default=0)
    late_arrivals = models.PositiveIntegerField(default=0)
    positive_reviews = models.PositiveIntegerField(default=0)

    skills = models.ManyToManyField("disco_app.Skill", blank=True)

    @property
    def disco_tier(self):
        rank = self.disco_rank

        if rank >= 90:
            return "Platinum"
        elif rank >= 80:
            return "Gold"
        elif rank >= 70:
            return "Silver"
        elif rank >= 55:
            return "Bronze"
        return "New"

    @property
    def disco_rank(self):
        score = 70

        # Completed shifts
        completed_count = self.shift_requests.filter(status="completed").count()
        score += completed_count * 3

        # Accepted shifts
        accepted_count = self.shift_requests.filter(status="accepted").count()
        score += accepted_count * 2

        # Pending/applying shows activity, but don't over-reward it
        pending_count = self.shift_requests.filter(status="pending").count()
        score += min(pending_count, 3)

        # Availability improves trust
        if self.availability_slots.exists():
            score += 5

        # Profile completeness
        if self.primary_role and self.primary_role != "not set":
            score += 3

        if self.bio:
            score += 3

        if self.year_started:
            score += 2

        # Penalise bad signals
        declined_count = self.shift_requests.filter(status="declined").count()
        score -= declined_count * 2

        cancelled_count = self.shift_requests.filter(status="cancelled").count()
        score -= cancelled_count * 5

        no_show_count = self.shift_requests.filter(status="no_show").count()
        score -= no_show_count * 12

        return max(0, min(score, 100))

    @property
    def full_name(self):
        full = f"{self.user.first_name} {self.user.last_name}".strip()

        if full:
            return full

        return self.user.username

    def recalculate_disco_rank(self):
        score = 70

        score += self.completed_shifts * 2
        score += self.positive_reviews * 3

        score -= self.cancelled_shifts * 5
        score -= self.late_arrivals * 4
        score -= self.no_shows * 15

        self.disco_rank = max(0, min(score, 100))
        self.save()

    def __str__(self):
        return self.user.username


class Availability(models.Model):
    DAY_CHOICES = [
        (0, "Monday"),
        (1, "Tuesday"),
        (2, "Wednesday"),
        (3, "Thursday"),
        (4, "Friday"),
        (5, "Saturday"),
        (6, "Sunday"),
    ]

    staff = models.ForeignKey(
        Staff, on_delete=models.CASCADE, related_name="availability_slots"
    )
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["day_of_week", "start_time"]
        unique_together = ["staff", "day_of_week", "start_time", "end_time"]

    def __str__(self):
        return f"{self.staff.user.username} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class Operator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)

    @property
    def full_name(self):
        full = f"{self.user.first_name} {self.user.last_name}".strip()

        if full:
            return full

        return self.user.username


def __str__(self):
    return self.company_name or self.user.username
