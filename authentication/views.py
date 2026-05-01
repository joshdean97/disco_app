from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Staff, Operator
from .forms import StaffRegistrationForm, OperatorRegistrationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# Create your views here.
# create staff and operator profiles when a user is created
def register(request):
    staff_form = StaffRegistrationForm()
    operator_form = OperatorRegistrationForm()
    user_type = None

    if request.method == "POST":
        user_type = request.POST.get("user_type")
        if user_type == "staff":
            staff_form = StaffRegistrationForm(request.POST)
            if staff_form.is_valid():
                user = staff_form.save()
                Staff.objects.create(
                    user=user,
                    primary_role=staff_form.cleaned_data.get("primary_role"),
                    year_started=staff_form.cleaned_data.get("year_started"),
                    bio=staff_form.cleaned_data.get("bio"),
                    travel_radius_miles=staff_form.cleaned_data.get("travel_radius_miles"),
                    is_available=staff_form.cleaned_data.get("is_available"),
                )
                return render(request, "authentication/register_success.html", {"user": user})
        elif user_type == "operator":
            operator_form = OperatorRegistrationForm(request.POST)
            if operator_form.is_valid():
                user = operator_form.save()
                Operator.objects.create(
                    user=user,
                    company_name=operator_form.cleaned_data.get("company_name"),
                )
                return render(request, "authentication/register_success.html", {"user": user})

    return render(
        request,
        "authentication/register.html",
        {
            "staff_form": staff_form,
            "operator_form": operator_form,
            "user_type": user_type,
        },
    )
    
def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)
        if user is not None:
            auth_login(request, user)
            return render(request, "authentication/login_success.html")
    return render(request, "authentication/login.html")

def logout(request):
    auth_logout(request)
    return render(request, "authentication/logout_success.html")

