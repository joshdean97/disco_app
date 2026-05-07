from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Staff, Operator, Availability


class StaffRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")
    primary_role = forms.ChoiceField(
        choices=Staff.ROLE_CHOICES,
        required=True,
        label="Primary Role",
    )
    year_started = forms.IntegerField(required=False, label="Year Started")
    bio = forms.CharField(widget=forms.Textarea, required=False, label="Bio")
    travel_radius_miles = forms.IntegerField(
        required=False, label="Travel Radius (miles)"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "primary_role",
            "year_started",
            "bio",
            "travel_radius_miles",
        ]


class OperatorRegistrationForm(UserCreationForm):
    company_name = forms.CharField(required=False, label="Company Name")
    first_name = forms.CharField(required=True, label="First Name")
    last_name = forms.CharField(required=True, label="Last Name")

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
            "first_name",
            "last_name",
            "company_name",
        ]


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ["day_of_week", "start_time", "end_time"]
        widgets = {
            "day_of_week": forms.Select(attrs={"class": "form-control"}),
            "start_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "end_time": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
        }
