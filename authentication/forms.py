from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Staff, Operator

class StaffRegistrationForm(UserCreationForm):
    primary_role = forms.ChoiceField(
        choices=Staff.ROLE_CHOICES,
        required=True,
        label="Primary Role",
    )
    year_started = forms.IntegerField(required=False, label="Year Started")
    bio = forms.CharField(widget=forms.Textarea, required=False, label="Bio")
    travel_radius_miles = forms.IntegerField(required=False, label="Travel Radius (miles)")
    is_available = forms.BooleanField(required=False, label="Available for Work")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "primary_role", "year_started", "bio", "travel_radius_miles", "is_available"]

class OperatorRegistrationForm(UserCreationForm):
    company_name = forms.CharField(required=False, label="Company Name")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2", "company_name"]

