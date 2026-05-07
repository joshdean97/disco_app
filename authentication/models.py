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

    @property
    def disco_tier(self):
        if self.disco_rank >= 90:
            return "Platinum"
        elif self.disco_rank >= 80:
            return "Gold"
        elif self.disco_rank >= 70:
            return "Silver"
        elif self.disco_rank >= 60:
            return "Bronze"
        return "Building"

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

    def __str__(self):
        return self.company_name or self.user.username
