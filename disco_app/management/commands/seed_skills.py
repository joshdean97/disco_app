from django.core.management.base import BaseCommand
from django.db import transaction

from authentication.models import Staff
from disco_app.models import Skill


class Command(BaseCommand):
    help = "Seed default skills and randomly assign them to staff profiles"

    DEFAULT_SKILLS = [
        ("Cocktail Making", "Bar"),
        ("Barista", "Bar"),
        ("Wine Service", "Service"),
        ("Tray Service", "Service"),
        ("Food Running", "Service"),
        ("EPOS", "Operations"),
        ("Host / Front Door", "Service"),
        ("Stock Count", "Operations"),
        ("Cellar Management", "Bar"),
        ("Opening Venue", "Operations"),
        ("Closing Venue", "Operations"),
        ("Allergen Knowledge", "Compliance"),
        ("Cash Handling", "Operations"),
        ("Table Service", "Service"),
        ("High Volume Service", "Service"),
        ("Cleaning Close Down", "Operations"),
        ("Basic Food Prep", "Kitchen"),
        ("Kitchen Porter", "Kitchen"),
        ("Passador / Meat Service", "Service"),
        ("Event Service", "Service"),
    ]

    def handle(self, *args, **options):
        with transaction.atomic():
            skills = []

            for name, category in self.DEFAULT_SKILLS:
                skill, created = Skill.objects.get_or_create(
                    name=name,
                    defaults={"category": category},
                )
                skills.append(skill)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created skill: {name}"))
                else:
                    self.stdout.write(f"Skill already exists: {name}")

            staff_members = Staff.objects.all()

            if not staff_members.exists():
                self.stdout.write(
                    self.style.WARNING(
                        "No staff found. Skills created but not assigned."
                    )
                )
                return

            for index, staff in enumerate(staff_members):
                staff.skills.clear()

                assigned_skills = []

                if staff.primary_role == "bartender":
                    assigned_skills = [
                        "Cocktail Making",
                        "EPOS",
                        "Stock Count",
                        "Cellar Management",
                        "Closing Venue",
                    ]

                elif staff.primary_role == "barista":
                    assigned_skills = [
                        "Barista",
                        "EPOS",
                        "Cash Handling",
                        "Opening Venue",
                    ]

                elif staff.primary_role == "waiting_staff":
                    assigned_skills = [
                        "Table Service",
                        "Tray Service",
                        "Food Running",
                        "Wine Service",
                        "Allergen Knowledge",
                    ]

                elif staff.primary_role == "chef":
                    assigned_skills = [
                        "Basic Food Prep",
                        "Kitchen Porter",
                        "Allergen Knowledge",
                        "Cleaning Close Down",
                    ]

                else:
                    assigned_skills = [
                        "EPOS",
                        "Table Service",
                        "Food Running",
                    ]

                # Add a little variation so everyone doesn't look cloned
                if index % 2 == 0:
                    assigned_skills.append("High Volume Service")

                if index % 3 == 0:
                    assigned_skills.append("Event Service")

                if index % 4 == 0:
                    assigned_skills.append("Opening Venue")

                matching_skills = Skill.objects.filter(name__in=assigned_skills)
                staff.skills.set(matching_skills)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Assigned {matching_skills.count()} skills to {staff.user.username}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Skill seeding complete. Disco workers now have flavour."
            )
        )
