from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from .models import Site, Shift, ShiftRequest
from authentication.models import Staff, Operator
from .forms import ShiftForm, SiteForm
from django.contrib import messages


@login_required
def edit_site(request, site_id):
    """Operator can edit their venue (Site)."""
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")
    site = get_object_or_404(Site, id=site_id, operators=operator)
    if request.method == "POST":
        form = SiteForm(request.POST, instance=site)
        if form.is_valid():
            form.save()
            messages.success(request, "Venue updated successfully.")
            return redirect("manage_sites")
    else:
        form = SiteForm(instance=site)
    return render(request, "operator/edit_site.html", {"form": form, "site": site})


def home(request):
    """Landing page with auth redirects."""
    if request.user.is_authenticated:
        # Redirect to appropriate dashboard based on user type
        try:
            Staff.objects.get(user=request.user)
            return redirect("staff_dashboard")
        except Staff.DoesNotExist:
            pass

        try:
            Operator.objects.get(user=request.user)
            return redirect("operator_dashboard")
        except Operator.DoesNotExist:
            pass

    return render(request, "disco_app/home.html")


@login_required
def staff_dashboard(request):
    """Staff member dashboard showing shifts and applications."""
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return redirect("register")

    # Get staff's shift requests
    pending_requests = staff.shift_requests.filter(status="pending")
    accepted_requests = staff.shift_requests.filter(status="accepted")
    completed_requests = staff.shift_requests.filter(status="completed")

    context = {
        "staff": staff,
        "pending_requests": pending_requests,
        "accepted_requests": accepted_requests,
        "completed_requests": completed_requests,
        "pending_count": pending_requests.count(),
        "accepted_count": accepted_requests.count(),
    }

    return render(request, "disco_app/staff_dashboard.html", context)


@login_required
def browse_shifts(request):
    """Staff browse and search for available shifts."""
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return redirect("register")

    shifts = Shift.objects.filter(status="open").select_related("site")

    today = datetime.now().date()
    shifts = shifts.filter(date__gte=today, date__lte=today + timedelta(days=14))

    city = request.GET.get("city")
    if city:
        shifts = shifts.filter(site__city__icontains=city)

    applied_shift_ids = staff.shift_requests.values_list("shift_id", flat=True)

    shifts_with_status = []

    for shift in shifts:
        applied_status = None

        if shift.id in applied_shift_ids:
            req = staff.shift_requests.get(shift_id=shift.id)
            applied_status = req.status

        is_recommended = (
            staff.primary_role
            and staff.primary_role != "not_set"
            and shift.role_required == staff.primary_role
        )

        shifts_with_status.append(
            {
                "shift": shift,
                "applied_status": applied_status,
                "is_recommended": is_recommended,
            }
        )

    shifts_with_status.sort(key=lambda item: item["is_recommended"], reverse=True)

    context = {
        "staff": staff,
        "shifts_with_status": shifts_with_status,
        "total_shifts": len(shifts_with_status),
    }

    return render(request, "disco_app/browse_shifts.html", context)


@login_required
@require_http_methods(["POST"])
def apply_for_shift(request, shift_id):
    """Staff applies for a shift."""
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return redirect("register")

    shift = get_object_or_404(Shift, id=shift_id, status="open")

    # Check if already applied
    existing = ShiftRequest.objects.filter(shift=shift, staff=staff).first()
    if existing:
        return redirect("browse_shifts")

    # Create shift request
    ShiftRequest.objects.create(shift=shift, staff=staff)

    return redirect("browse_shifts")


@login_required
def operator_dashboard(request):
    """Operator dashboard showing shifts and applications."""
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")

    # Get operator's sites
    sites = operator.sites.all()

    # Get shifts for operator's sites
    open_shifts = Shift.objects.filter(site__in=sites, status="open")
    confirmed_shifts = Shift.objects.filter(site__in=sites, status="confirmed")
    completed_shifts = Shift.objects.filter(site__in=sites, status="completed")

    # Get pending shift requests across operator's sites
    pending_requests = ShiftRequest.objects.filter(
        shift__site__in=sites, status="pending"
    ).select_related("staff", "shift", "shift__site")

    context = {
        "operator": operator,
        "sites": sites,
        "open_shifts": open_shifts,
        "confirmed_shifts": confirmed_shifts,
        "completed_shifts": completed_shifts,
        "pending_requests": pending_requests,
        "pending_count": pending_requests.count(),
        "open_count": open_shifts.count(),
    }

    return render(request, "disco_app/operator_dashboard.html", context)


@login_required
def post_shift(request):
    """Operator posts a new shift."""
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")

    sites = operator.sites.all()

    if request.method == "POST":
        form = ShiftForm(request.POST)
        form.fields["site"].queryset = sites

        if form.is_valid():
            shift = form.save(commit=False)
            shift.site = form.cleaned_data["site"]
            shift.save()
            messages.success(request, "Shift posted successfully.")
            return redirect("operator_dashboard")
    else:
        form = ShiftForm()
        form.fields["site"].queryset = sites

    return render(
        request,
        "disco_app/post_shift.html",
        {
            "form": form,
            "operator": operator,
        },
    )


@login_required
def manage_shift_requests(request, shift_id):
    """Operator view pending applications for a shift."""
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")

    shift = get_object_or_404(Shift, id=shift_id, site__in=operator.sites.all())
    requests = shift.applications.filter(status="pending").select_related("staff")

    context = {
        "shift": shift,
        "requests": requests,
        "operator": operator,
    }

    return render(request, "disco_app/manage_shift_requests.html", context)


@login_required
@require_http_methods(["POST"])
def respond_to_request(request, request_id):
    """Operator accepts or declines a shift request."""
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")

    sr = get_object_or_404(
        ShiftRequest, id=request_id, shift__site__in=operator.sites.all()
    )
    action = request.POST.get("action")

    if action == "accept":
        sr.status = "accepted"
        sr.shift.status = "confirmed"
        sr.shift.save()
        sr.responded_at = datetime.now()
        sr.save()
    elif action == "decline":
        sr.status = "declined"
        sr.responded_at = datetime.now()
        sr.save()

    return redirect("operator_dashboard")


@login_required
def manage_sites(request):
    """Operator can view, add, and edit their venues (Sites)."""
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")

    sites = operator.sites.all()
    form = SiteForm()
    if request.method == "POST":
        form = SiteForm(request.POST)
        if form.is_valid():
            site = form.save(commit=False)
            # Geocode address
            from geopy.geocoders import Nominatim

            geolocator = Nominatim(user_agent="disco_app")
            address_str = f"{site.address}, {site.city}, {site.postcode}"
            try:
                location = geolocator.geocode(address_str)
                if location:
                    site.latitude = location.latitude
                    site.longitude = location.longitude
            except Exception:
                pass
            site.save()
            site.operators.add(operator)
            from django.contrib import messages

            messages.success(request, "Venue added successfully.")
            return redirect("manage_sites")
    return render(
        request,
        "disco_app/manage_sites.html",
        {"sites": sites, "form": form, "operator": operator},
    )


@login_required
def find_staff_for_shift(request, shift_id):
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")

    shift = get_object_or_404(Shift, id=shift_id, site__in=operator.sites.all())

    # Convert shift date to weekday (0 = Monday)
    day_of_week = shift.date.weekday()

    # Base query: match role
    staff_qs = Staff.objects.filter(primary_role=shift.role_required)

    # Match availability
    staff_qs = staff_qs.filter(
        availability_slots__day_of_week=day_of_week,
        availability_slots__start_time__lte=shift.start_time,
        availability_slots__end_time__gte=shift.end_time,
    ).distinct()

    context = {
        "shift": shift,
        "staff_results": staff_qs,
    }

    return render(request, "disco_app/find_staff.html", context)


@login_required
def staff_profile(request, staff_id):
    staff_member = get_object_or_404(Staff, id=staff_id)

    availability_slots = staff_member.availability_slots.all()

    requests = staff_member.shift_requests.select_related("shift", "shift__site")

    pending_requests = requests.filter(status="pending")
    accepted_requests = requests.filter(status="accepted")
    completed_requests = requests.filter(status="completed")
    cancelled_requests = requests.filter(status="cancelled")

    accepted_count = accepted_requests.count()
    completed_count = completed_requests.count()
    cancelled_count = cancelled_requests.count()

    if accepted_count > 0:
        reliability = (
            (completed_count - (cancelled_count * 0.5)) / accepted_count
        ) * 100
        reliability = max(0, min(100, reliability))
    else:
        reliability = None

    context = {
        "staff_member": staff_member,
        "availability_slots": availability_slots,
        "pending_requests": pending_requests,
        "accepted_requests": accepted_requests,
        "completed_requests": completed_requests,
        "accepted_count": accepted_count,
        "completed_count": completed_count,
        "pending_count": pending_requests.count(),
        "reliability": reliability,
    }

    return render(request, "disco_app/profile.html", context)


@login_required
def my_profile(request):
    try:
        staff = Staff.objects.get(user=request.user)
    except Staff.DoesNotExist:
        return redirect("register")

    if request.method == "POST":
        staff.primary_role = request.POST.get("primary_role")
        staff.year_started = request.POST.get("year_started") or None
        staff.bio = request.POST.get("bio", "")
        staff.travel_radius_miles = request.POST.get("travel_radius_miles") or 5
        staff.save()

        messages.success(request, "Profile updated successfully.")
        return redirect("my_profile")

    availability_slots = staff.availability_slots.all()

    return render(
        request,
        "disco_app/my_profile.html",
        {
            "staff": staff,
            "availability_slots": availability_slots,
        },
    )


@login_required
@require_http_methods(["POST"])
def invite_staff_to_shift(request, shift_id, staff_id):
    try:
        operator = Operator.objects.get(user=request.user)
    except Operator.DoesNotExist:
        return redirect("register")

    shift = get_object_or_404(
        Shift, id=shift_id, site__in=operator.sites.all(), status="open"
    )

    staff = get_object_or_404(Staff, id=staff_id)

    existing_request = ShiftRequest.objects.filter(shift=shift, staff=staff).first()

    if existing_request:
        messages.info(
            request, "This staff member already has a request for this shift."
        )
        return redirect("find_staff_for_shift", shift_id=shift.id)

    ShiftRequest.objects.create(shift=shift, staff=staff, status="pending")

    messages.success(request, f"{staff.user.username} has been invited to this shift.")

    return redirect("find_staff_for_shift", shift_id=shift.id)
