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
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


class Operator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.company_name or self.user.username
