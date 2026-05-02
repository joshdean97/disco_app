from django import forms
from .models import Shift, ShiftRequest, Site


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["site", "role_required", "date", "start_time", "end_time", "hourly_rate", "notes"]
        widgets = {
            "site": forms.Select(attrs={"class": "form-control"}),
            "role_required": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "hourly_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ShiftRequestForm(forms.ModelForm):
    class Meta:
        model = ShiftRequest
        fields = []


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["name", "address", "city", "postcode", "venue_type"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postcode": forms.TextInput(attrs={"class": "form-control"}),
            "venue_type": forms.Select(attrs={"class": "form-control"}),
        }
