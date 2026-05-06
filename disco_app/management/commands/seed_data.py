from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from authentication.models import Staff, Operator, Availability
from disco_app.models import Site, Shift, ShiftRequest


class Command(BaseCommand):
    help = "Seed the database with test users, venues, availability, shifts, and applications."

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding database...")

        # Clear old test data
        ShiftRequest.objects.all().delete()
        Shift.objects.all().delete()
        Site.objects.all().delete()
        Availability.objects.all().delete()
        Staff.objects.all().delete()
        Operator.objects.all().delete()
        User.objects.filter(username__startswith="test_").delete()

        # Create operator user
        operator_user = User.objects.create_user(
            username="test_operator", email="operator@test.com", password="password123"
        )

        operator = Operator.objects.create(
            user=operator_user, company_name="Josh's Grill Leeds"
        )

        # Create sites
        site_1 = Site.objects.create(
            name="Josh's Grill Leeds",
            address="1 Test Street",
            city="Leeds",
            postcode="LS1 1AA",
            venue_type="restaurant",
            latitude=53.8008,
            longitude=-1.5491,
        )
        site_1.operators.add(operator)

        site_2 = Site.objects.create(
            name="Disco Bar",
            address="22 Test Road",
            city="Leeds",
            postcode="LS2 2BB",
            venue_type="bar",
            latitude=53.8015,
            longitude=-1.5480,
        )
        site_2.operators.add(operator)

        # Create staff users
        staff_data = [
            ("test_chef", "chef"),
            ("test_bartender", "bartender"),
            ("test_waiter", "waiting_staff"),
            ("test_barista", "barista"),
            ("test_flexible", "waiting_staff"),
        ]

        staff_members = []

        for username, role in staff_data:
            user = User.objects.create_user(
                username=username, email=f"{username}@test.com", password="password123"
            )

            staff = Staff.objects.create(
                user=user,
                primary_role=role,
                year_started=2021,
                bio=f"Experienced {role.replace('_', ' ')} available for shifts.",
                travel_radius_miles=10,
            )

            staff_members.append(staff)

        # Add availability
        # Monday-Friday availability for most staff
        for staff in staff_members:
            for day in range(0, 5):
                Availability.objects.create(
                    staff=staff,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(23, 0),
                )

        # Extra weekend availability for bartender and waiter
        for staff in staff_members[1:3]:
            Availability.objects.create(
                staff=staff,
                day_of_week=5,
                start_time=time(16, 0),
                end_time=time(23, 59),
            )

            Availability.objects.create(
                staff=staff,
                day_of_week=6,
                start_time=time(12, 0),
                end_time=time(22, 0),
            )

        today = date.today()

        # Create shifts
        shifts = [
            Shift.objects.create(
                site=site_1,
                role_required="chef",
                date=today + timedelta(days=1),
                start_time=time(10, 0),
                end_time=time(18, 0),
                hourly_rate=15.00,
                status="open",
                notes="Prep and service support.",
            ),
            Shift.objects.create(
                site=site_1,
                role_required="waiting_staff",
                date=today + timedelta(days=2),
                start_time=time(12, 0),
                end_time=time(22, 0),
                hourly_rate=12.50,
                status="open",
                notes="Busy dinner service.",
            ),
            Shift.objects.create(
                site=site_2,
                role_required="bartender",
                date=today + timedelta(days=3),
                start_time=time(17, 0),
                end_time=time(23, 0),
                hourly_rate=13.50,
                status="open",
                notes="Cocktail experience preferred.",
            ),
            Shift.objects.create(
                site=site_2,
                role_required="barista",
                date=today + timedelta(days=4),
                start_time=time(8, 0),
                end_time=time(14, 0),
                hourly_rate=12.00,
                status="open",
                notes="Morning coffee shift.",
            ),
        ]

        # Create one pending application
        ShiftRequest.objects.create(
            shift=shifts[1],
            staff=staff_members[2],
            status="pending",
        )

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
        self.stdout.write("")
        self.stdout.write("Login details:")
        self.stdout.write("Operator: test_operator / password123")
        self.stdout.write("Chef: test_chef / password123")
        self.stdout.write("Bartender: test_bartender / password123")
        self.stdout.write("Waiter: test_waiter / password123")
        self.stdout.write("Barista: test_barista / password123")
