from django.test import TestCase

# Create your tests here.
from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.db import IntegrityError

from authentication.models import Staff, Operator, Availability
from disco_app.models import Site, Shift, ShiftRequest


class DiscoMVPTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_user(
            username="staff1",
            email="staff1@test.com",
            password="testpass123",
        )
        self.staff = Staff.objects.create(
            user=self.staff_user,
            primary_role="bartender",
            year_started=2020,
            bio="Experienced bartender.",
            travel_radius_miles=10,
        )

        self.staff_user_2 = User.objects.create_user(
            username="staff2",
            email="staff2@test.com",
            password="testpass123",
        )
        self.staff_2 = Staff.objects.create(
            user=self.staff_user_2,
            primary_role="bartender",
            year_started=2021,
            bio="Reliable bar staff.",
            travel_radius_miles=10,
        )

        self.operator_user = User.objects.create_user(
            username="operator1",
            email="operator1@test.com",
            password="testpass123",
        )
        self.operator = Operator.objects.create(
            user=self.operator_user,
            company_name="Demo Hospitality",
        )

        self.other_operator_user = User.objects.create_user(
            username="operator2",
            email="operator2@test.com",
            password="testpass123",
        )
        self.other_operator = Operator.objects.create(
            user=self.other_operator_user,
            company_name="Other Hospitality",
        )

        self.site = Site.objects.create(
            name="Demo Bar",
            address="1 Demo Street",
            city="Leeds",
            postcode="LS1 1AA",
            venue_type="bar",
        )
        self.site.operators.add(self.operator)

        self.other_site = Site.objects.create(
            name="Other Bar",
            address="2 Other Street",
            city="Manchester",
            postcode="M1 1AA",
            venue_type="bar",
        )
        self.other_site.operators.add(self.other_operator)

        self.shift = Shift.objects.create(
            site=self.site,
            role_required="bartender",
            date=date.today() + timedelta(days=3),
            start_time=time(18, 0),
            end_time=time(23, 0),
            hourly_rate=Decimal("14.00"),
            status="open",
            notes="Busy Saturday shift.",
        )

        self.other_shift = Shift.objects.create(
            site=self.other_site,
            role_required="bartender",
            date=date.today() + timedelta(days=3),
            start_time=time(18, 0),
            end_time=time(23, 0),
            hourly_rate=Decimal("14.00"),
            status="open",
        )

    def login_staff(self):
        self.client.login(username="staff1", password="testpass123")

    def login_operator(self):
        self.client.login(username="operator1", password="testpass123")

    def reverse_or_skip(self, name, *args):
        try:
            return reverse(name, args=args)
        except NoReverseMatch:
            self.skipTest(f"URL name '{name}' does not exist yet.")

    def test_staff_dashboard_requires_login(self):
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_operator_dashboard_requires_login(self):
        response = self.client.get(reverse("operator_dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_staff_dashboard_loads_for_staff(self):
        self.login_staff()
        response = self.client.get(reverse("staff_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_operator_dashboard_loads_for_operator(self):
        self.login_operator()
        response = self.client.get(reverse("operator_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_browse_shifts_only_shows_open_shifts(self):
        Shift.objects.create(
            site=self.site,
            role_required="chef",
            date=date.today() + timedelta(days=3),
            start_time=time(10, 0),
            end_time=time(16, 0),
            hourly_rate=Decimal("15.00"),
            status="open",
        )

        Shift.objects.create(
            site=self.site,
            role_required="bartender",
            date=date.today() + timedelta(days=3),
            start_time=time(10, 0),
            end_time=time(16, 0),
            hourly_rate=Decimal("15.00"),
            status="confirmed",
        )

        self.login_staff()
        response = self.client.get(reverse("browse_shifts"))

        self.assertEqual(response.status_code, 200)
        shifts_with_status = response.context["shifts_with_status"]

        self.assertTrue(any(item["shift"] == self.shift for item in shifts_with_status))
        self.assertTrue(
            any(item["shift"].role_required == "chef" for item in shifts_with_status)
        )
        self.assertFalse(
            any(item["shift"].status == "confirmed" for item in shifts_with_status)
        )

    def test_staff_can_apply_for_open_shift(self):
        self.login_staff()

        response = self.client.post(reverse("apply_for_shift", args=[self.shift.id]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ShiftRequest.objects.filter(
                shift=self.shift,
                staff=self.staff,
                status="pending",
            ).exists()
        )

    def test_staff_cannot_apply_twice_for_same_shift(self):
        self.login_staff()

        self.client.post(reverse("apply_for_shift", args=[self.shift.id]))
        self.client.post(reverse("apply_for_shift", args=[self.shift.id]))

        self.assertEqual(
            ShiftRequest.objects.filter(shift=self.shift, staff=self.staff).count(),
            1,
        )

    def test_database_prevents_duplicate_shift_requests(self):
        ShiftRequest.objects.create(shift=self.shift, staff=self.staff)

        with self.assertRaises(IntegrityError):
            ShiftRequest.objects.create(shift=self.shift, staff=self.staff)

    def test_staff_cannot_apply_for_confirmed_shift(self):
        self.shift.status = "confirmed"
        self.shift.save()

        self.login_staff()
        response = self.client.post(reverse("apply_for_shift", args=[self.shift.id]))

        self.assertEqual(response.status_code, 404)
        self.assertFalse(
            ShiftRequest.objects.filter(shift=self.shift, staff=self.staff).exists()
        )

    def test_operator_only_sees_own_shifts_on_dashboard(self):
        self.login_operator()
        response = self.client.get(reverse("operator_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Demo Bar")
        self.assertNotContains(response, "Other Bar")

    def test_operator_can_view_requests_for_own_shift(self):
        ShiftRequest.objects.create(shift=self.shift, staff=self.staff)

        self.login_operator()
        response = self.client.get(
            reverse("manage_shift_requests", args=[self.shift.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.staff.user.username)

    def test_operator_cannot_view_requests_for_other_operator_shift(self):
        self.login_operator()
        response = self.client.get(
            reverse("manage_shift_requests", args=[self.other_shift.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_operator_can_decline_request(self):
        request_obj = ShiftRequest.objects.create(
            shift=self.shift,
            staff=self.staff,
            status="pending",
        )

        self.login_operator()
        response = self.client.post(
            reverse("respond_to_request", args=[request_obj.id]),
            {"action": "decline"},
        )

        request_obj.refresh_from_db()
        self.shift.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(request_obj.status, "declined")
        self.assertEqual(self.shift.status, "open")

    def test_operator_can_accept_request_and_confirm_shift(self):
        request_obj = ShiftRequest.objects.create(
            shift=self.shift,
            staff=self.staff,
            status="pending",
        )

        self.login_operator()
        response = self.client.post(
            reverse("respond_to_request", args=[request_obj.id]),
            {"action": "accept"},
        )

        request_obj.refresh_from_db()
        self.shift.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(request_obj.status, "accepted")
        self.assertEqual(self.shift.status, "confirmed")

    def test_accepting_one_request_declines_other_pending_requests_for_same_shift(self):
        request_1 = ShiftRequest.objects.create(
            shift=self.shift,
            staff=self.staff,
            status="pending",
        )
        request_2 = ShiftRequest.objects.create(
            shift=self.shift,
            staff=self.staff_2,
            status="pending",
        )

        self.login_operator()
        self.client.post(
            reverse("respond_to_request", args=[request_1.id]),
            {"action": "accept"},
        )

        request_1.refresh_from_db()
        request_2.refresh_from_db()
        self.shift.refresh_from_db()

        self.assertEqual(request_1.status, "accepted")
        self.assertEqual(request_2.status, "declined")
        self.assertEqual(self.shift.status, "confirmed")

    def test_operator_cannot_accept_request_for_other_operator_shift(self):
        other_request = ShiftRequest.objects.create(
            shift=self.other_shift,
            staff=self.staff,
            status="pending",
        )

        self.login_operator()
        response = self.client.post(
            reverse("respond_to_request", args=[other_request.id]),
            {"action": "accept"},
        )

        other_request.refresh_from_db()
        self.other_shift.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(other_request.status, "pending")
        self.assertEqual(self.other_shift.status, "open")

    def test_operator_can_post_shift_for_own_site(self):
        self.login_operator()

        response = self.client.post(
            reverse("post_shift"),
            {
                "site": self.site.id,
                "role_required": "bartender",
                "date": date.today() + timedelta(days=5),
                "start_time": "17:00",
                "end_time": "23:00",
                "hourly_rate": "13.50",
                "notes": "Test shift.",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Shift.objects.filter(
                site=self.site,
                role_required="bartender",
                hourly_rate=Decimal("13.50"),
            ).exists()
        )

    def test_operator_cannot_post_shift_for_someone_elses_site(self):
        self.login_operator()

        self.client.post(
            reverse("post_shift"),
            {
                "site": self.other_site.id,
                "role_required": "bartender",
                "date": date.today() + timedelta(days=5),
                "start_time": "17:00",
                "end_time": "23:00",
                "hourly_rate": "13.50",
                "notes": "Should not be allowed.",
            },
        )

        self.assertFalse(
            Shift.objects.filter(
                site=self.other_site,
                notes="Should not be allowed.",
            ).exists()
        )

    def test_operator_can_add_site(self):
        self.login_operator()

        response = self.client.post(
            reverse("manage_sites"),
            {
                "name": "New Venue",
                "address": "10 New Street",
                "city": "Leeds",
                "postcode": "LS2 2BB",
                "venue_type": "restaurant",
            },
        )

        self.assertEqual(response.status_code, 302)

        new_site = Site.objects.get(name="New Venue")
        self.assertTrue(new_site.operators.filter(id=self.operator.id).exists())

    def test_operator_can_edit_own_site(self):
        self.login_operator()

        response = self.client.post(
            reverse("edit_site", args=[self.site.id]),
            {
                "name": "Updated Demo Bar",
                "address": self.site.address,
                "city": self.site.city,
                "postcode": self.site.postcode,
                "venue_type": self.site.venue_type,
            },
        )

        self.site.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.site.name, "Updated Demo Bar")

    def test_operator_cannot_edit_other_operator_site(self):
        self.login_operator()

        response = self.client.post(
            reverse("edit_site", args=[self.other_site.id]),
            {
                "name": "Hacked Venue",
                "address": self.other_site.address,
                "city": self.other_site.city,
                "postcode": self.other_site.postcode,
                "venue_type": self.other_site.venue_type,
            },
        )

        self.other_site.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertNotEqual(self.other_site.name, "Hacked Venue")

    def test_staff_can_manage_availability(self):
        self.login_staff()

        response = self.client.post(
            reverse("manage_availability"),
            {
                "day_of_week": 5,
                "start_time": "10:00",
                "end_time": "18:00",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Availability.objects.filter(
                staff=self.staff,
                day_of_week=5,
                start_time="10:00",
                end_time="18:00",
            ).exists()
        )

    def test_staff_can_delete_own_availability(self):
        availability = Availability.objects.create(
            staff=self.staff,
            day_of_week=5,
            start_time=time(10, 0),
            end_time=time(18, 0),
        )

        self.login_staff()
        response = self.client.get(
            reverse("delete_availability", args=[availability.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Availability.objects.filter(id=availability.id).exists())

    def test_staff_cannot_delete_someone_elses_availability(self):
        availability = Availability.objects.create(
            staff=self.staff_2,
            day_of_week=5,
            start_time=time(10, 0),
            end_time=time(18, 0),
        )

        self.login_staff()
        response = self.client.get(
            reverse("delete_availability", args=[availability.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Availability.objects.filter(id=availability.id).exists())

    def test_mark_shift_completed_updates_shift_and_request_if_url_exists(self):
        request_obj = ShiftRequest.objects.create(
            shift=self.shift,
            staff=self.staff,
            status="accepted",
        )
        self.shift.status = "confirmed"
        self.shift.save()

        self.login_operator()
        url = self.reverse_or_skip("mark_shift_completed", self.shift.id)

        response = self.client.post(url)

        request_obj.refresh_from_db()
        self.shift.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.shift.status, "completed")
        self.assertEqual(request_obj.status, "completed")

    def test_cancel_booking_reopens_shift_and_cancels_request_if_url_exists(self):
        request_obj = ShiftRequest.objects.create(
            shift=self.shift,
            staff=self.staff,
            status="accepted",
        )
        self.shift.status = "confirmed"
        self.shift.save()

        self.login_operator()
        url = self.reverse_or_skip("cancel_shift_booking", self.shift.id)

        response = self.client.post(url)

        request_obj.refresh_from_db()
        self.shift.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.shift.status, "open")
        self.assertEqual(request_obj.status, "cancelled")
