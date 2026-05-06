from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Staff, Operator, Availability
from .forms import StaffRegistrationForm, OperatorRegistrationForm, AvailabilityForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout


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
                    travel_radius_miles=staff_form.cleaned_data.get(
                        "travel_radius_miles"
                    ),
                )

                return render(
                    request, "authentication/register_success.html", {"user": user}
                )

        elif user_type == "operator":
            operator_form = OperatorRegistrationForm(request.POST)

            if operator_form.is_valid():
                user = operator_form.save()

                Operator.objects.create(
                    user=user,
                    company_name=operator_form.cleaned_data.get("company_name"),
                )

                return render(
                    request, "authentication/register_success.html", {"user": user}
                )

    return render(
        request,
        "authentication/register.html",
        {
            "staff_form": staff_form,
            "operator_form": operator_form,
            "user_type": user_type,
        },
    )


@login_required
def manage_availability(request):
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return redirect("register")

    availabilities = staff.availability_slots.all()
    form = AvailabilityForm()

    if request.method == "POST":
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.staff = staff
            availability.save()
            return redirect("manage_availability")

    return render(
        request,
        "authentication/manage_availability.html",
        {
            "form": form,
            "availabilities": availabilities,
            "staff": staff,
        },
    )


@login_required
def delete_availability(request, availability_id):
    try:
        staff = Staff.objects.get(user=request.user)
        availability = Availability.objects.get(id=availability_id, staff=staff)
        availability.delete()
    except (Staff.DoesNotExist, Availability.DoesNotExist):
        pass

    return redirect("manage_availability")


def login(request):
    error_message = None
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(
            f"Login attempt: email={email}, password={'*' * len(password) if password else 'None'}"
        )

        try:
            user_obj = User.objects.get(email=email)
            print(f"User found: {user_obj.username}")

            user = authenticate(request, username=user_obj.username, password=password)
            print(f"Authenticate result: {user}")

            if user is not None:
                auth_login(request, user)
                print("Login successful")
                return render(request, "authentication/login_success.html")
            else:
                error_message = "Invalid email or password."
                print("Authentication failed - password incorrect")
        except User.DoesNotExist:
            error_message = "Invalid email or password."
            print(f"User not found: {email}")

    return render(
        request, "authentication/login.html", {"error_message": error_message}
    )


def logout(request):
    auth_logout(request)
    return redirect("home")
