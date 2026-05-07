from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from authentication.models import Staff, Operator, Availability
from disco_app.models import Site, Shift, ShiftRequest


class Command(BaseCommand):
    help = "Seed Disco with demo operators, staff, venues, shifts, requests, and completed history."

    def handle(self, *args, **kwargs):
        self.stdout.write("Clearing old demo data...")

        User.objects.filter(username__startswith="demo_").delete()
        Site.objects.filter(name__startswith="Demo").delete()

        self.stdout.write("Creating demo operators...")

        operator_users = []
        operator_data = [
            ("demo_operator_josh", "Josh", "Shepherd", "Josh's Hospitality Group"),
            ("demo_operator_sophie", "Sophie", "Carter", "Northern Venues Ltd"),
            ("demo_operator_amy", "Amy", "Walsh", "Leeds Event Bars"),
        ]

        for username, first, last, company in operator_data:
            user = User.objects.create_user(
                username=username,
                email=f"{username}@disco.test",
                password="password123",
                first_name=first,
                last_name=last,
            )

            operator = Operator.objects.create(
                user=user,
                company_name=company,
            )
            operator_users.append(operator)

        self.stdout.write("Creating demo venues...")

        venues = [
            {
                "operator": operator_users[0],
                "name": "Demo Josh's Grill Leeds",
                "address": "1 Greek Street",
                "city": "Leeds",
                "postcode": "LS1 5SH",
                "venue_type": "restaurant",
                "latitude": 53.7997,
                "longitude": -1.5492,
            },
            {
                "operator": operator_users[0],
                "name": "Demo Josh's Grill Merrion Centre",
                "address": "Merrion Street",
                "city": "Leeds",
                "postcode": "LS2 8NG",
                "venue_type": "restaurant",
                "latitude": 53.8025,
                "longitude": -1.5438,
            },
            {
                "operator": operator_users[1],
                "name": "Demo Northern Tap House",
                "address": "Call Lane",
                "city": "Leeds",
                "postcode": "LS1 7BT",
                "venue_type": "bar",
                "latitude": 53.7955,
                "longitude": -1.5416,
            },
            {
                "operator": operator_users[2],
                "name": "Demo Arena Events Bar",
                "address": "Clay Pit Lane",
                "city": "Leeds",
                "postcode": "LS2 8BY",
                "venue_type": "bar",
                "latitude": 53.8039,
                "longitude": -1.5421,
            },
        ]

        sites = []

        for venue in venues:
            operator = venue.pop("operator")
            site = Site.objects.create(**venue)
            site.operators.add(operator)
            sites.append(site)

        self.stdout.write("Creating demo staff...")

        staff_rows = [
            (
                "sarah",
                "Parker",
                "waiting_staff",
                2019,
                "Reliable floor staff with strong restaurant experience.",
                5,
                53.8000,
                -1.5480,
            ),
            (
                "tom",
                "Ellis",
                "bartender",
                2020,
                "Cocktail bartender, fast under pressure.",
                4,
                53.7980,
                -1.5500,
            ),
            (
                "mia",
                "Brooks",
                "chef",
                2017,
                "Prep chef and grill experience.",
                6,
                53.8060,
                -1.5440,
            ),
            (
                "dan",
                "Taylor",
                "barista",
                2021,
                "Coffee-focused, brunch and cafe shifts.",
                3,
                53.8010,
                -1.5600,
            ),
            (
                "leah",
                "Morgan",
                "waiting_staff",
                2022,
                "Confident with busy service and upselling.",
                7,
                53.7900,
                -1.5300,
            ),
            (
                "ryan",
                "Cooper",
                "bartender",
                2018,
                "Event bar and late-night venue experience.",
                8,
                53.8100,
                -1.5350,
            ),
            (
                "ella",
                "Reed",
                "waiting_staff",
                2023,
                "Newer worker, great availability.",
                4,
                53.7970,
                -1.5550,
            ),
            (
                "jack",
                "Hughes",
                "chef",
                2016,
                "Senior chef, strong grill and prep background.",
                10,
                53.8200,
                -1.5700,
            ),
            (
                "nina",
                "Patel",
                "barista",
                2020,
                "Cafe, bakery, and till experience.",
                5,
                53.7950,
                -1.5450,
            ),
            (
                "omar",
                "Khan",
                "waiting_staff",
                2018,
                "Hotel, events, and restaurant floor experience.",
                6,
                53.8040,
                -1.5480,
            ),
            (
                "chloe",
                "Evans",
                "bartender",
                2022,
                "High-volume bar shifts and events.",
                5,
                53.7990,
                -1.5400,
            ),
            (
                "ben",
                "Walker",
                "chef",
                2019,
                "Line chef, prep, and closing experience.",
                7,
                53.7870,
                -1.5600,
            ),
        ]

        staff_members = []

        for first, last, role, year, bio, radius, lat, lng in staff_rows:
            username = f"demo_{first.lower()}_{last.lower()}"

            user = User.objects.create_user(
                username=username,
                email=f"{username}@disco.test",
                password="password123",
                first_name=first.title(),
                last_name=last.title(),
            )

            staff = Staff.objects.create(
                user=user,
                primary_role=role,
                year_started=year,
                bio=bio,
                travel_radius_miles=radius,
                postcode="LS1",
                latitude=lat,
                longitude=lng,
            )

            staff_members.append(staff)

            for day in range(0, 7):
                Availability.objects.create(
                    staff=staff,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(23, 0),
                )

        self.stdout.write("Creating demo shifts...")

        today = date.today()
        roles = ["waiting_staff", "bartender", "chef", "barista"]
        rates = {
            "waiting_staff": Decimal("13.00"),
            "bartender": Decimal("14.00"),
            "chef": Decimal("16.50"),
            "barista": Decimal("12.50"),
        }

        shifts = []

        for i in range(18):
            role = roles[i % len(roles)]
            site = sites[i % len(sites)]
            shift_date = today + timedelta(days=(i % 10) + 1)

            shift = Shift.objects.create(
                site=site,
                role_required=role,
                date=shift_date,
                start_time=time(15, 0) if i % 2 == 0 else time(10, 0),
                end_time=time(22, 0) if i % 2 == 0 else time(16, 0),
                hourly_rate=rates[role],
                status="open",
                notes="Demo seeded shift.",
            )

            shifts.append(shift)

        self.stdout.write("Creating demo applications and invites...")

        for i, shift in enumerate(shifts[:10]):
            matching_staff = [
                staff
                for staff in staff_members
                if staff.primary_role == shift.role_required
            ]

            for staff in matching_staff[:3]:
                ShiftRequest.objects.get_or_create(
                    shift=shift,
                    staff=staff,
                    defaults={
                        "status": "pending",
                        "source": "application" if i % 2 == 0 else "invite",
                    },
                )

        self.stdout.write("Creating confirmed shifts...")

        for i, shift in enumerate(shifts[10:14]):
            matching_staff = [
                staff
                for staff in staff_members
                if staff.primary_role == shift.role_required
            ]

            if not matching_staff:
                continue

            staff = matching_staff[0]

            ShiftRequest.objects.create(
                shift=shift,
                staff=staff,
                status="accepted",
                source="invite",
            )

            shift.status = "confirmed"
            shift.save()

        self.stdout.write("Creating completed shift history...")

        for i in range(20):
            staff = staff_members[i % len(staff_members)]
            site = sites[i % len(sites)]

            completed_shift = Shift.objects.create(
                site=site,
                role_required=staff.primary_role,
                date=today - timedelta(days=i + 1),
                start_time=time(12, 0),
                end_time=time(20, 0),
                hourly_rate=rates.get(staff.primary_role, Decimal("13.00")),
                status="completed",
                notes="Completed demo shift.",
            )

            ShiftRequest.objects.create(
                shift=completed_shift,
                staff=staff,
                status="completed",
                source="invite",
            )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
        self.stdout.write("Demo password for all accounts: password123")
