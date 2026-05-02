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

    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name="availability_slots")
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
