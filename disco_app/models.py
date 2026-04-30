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
        ("requested", "Requested"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    site = models.ForeignKey(
        "disco_app.Site",
        on_delete=models.CASCADE,
        related_name="shifts",
    )

    worker = models.ForeignKey(
        "authentication.Staff",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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

    def __str__(self):
        return f"{self.role_required} at {self.site.name} on {self.date}"
