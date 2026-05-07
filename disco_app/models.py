from django.db import models


class Site(models.Model):
    operators = models.ManyToManyField(
        "authentication.Operator",
        related_name="sites",
    )
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    venue_type = models.CharField(
        max_length=50,
        choices=[
            ("restaurant", "Restaurant"),
            ("bar", "Bar"),
            ("pub", "Pub"),
            ("club", "Club"),
            ("hotel", "Hotel"),
            ("cafe", "Cafe"),
            ("other", "Other"),
        ],
        default="restaurant",
    )

    def __str__(self):
        return self.name


class Shift(models.Model):
    ROLE_CHOICES = [
        ("chef", "Chef"),
        ("bartender", "Bartender"),
        ("waiting_staff", "Waiting Staff"),
        ("barista", "Barista"),
    ]

    STATUS_CHOICES = [
        ("open", "Open"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    site = models.ForeignKey(
        "disco_app.Site",
        on_delete=models.CASCADE,
        related_name="shifts",
    )

    role_required = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
    )

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Hourly rate offered for this shift",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="open",
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-start_time"]

    def __str__(self):
        return (
            f"{self.get_role_required_display()} "
            f"at {self.site.name} "
            f"on {self.date}"
        )


class ShiftRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    SOURCE_CHOICES = [
        ("application", "Application"),
        ("invite", "Invite"),
    ]

    shift = models.ForeignKey(
        Shift,
        on_delete=models.CASCADE,
        related_name="applications",
    )

    staff = models.ForeignKey(
        "authentication.Staff",
        on_delete=models.CASCADE,
        related_name="shift_requests",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default="application",
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-applied_at"]
        unique_together = ["shift", "staff"]

    def __str__(self):
        return f"{self.staff.user.username} → {self.shift} ({self.status})"
