
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Site, Shift, ShiftRequest
from authentication.models import Staff, Operator
from .forms import ShiftForm, ShiftRequestForm, SiteForm
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
    
    # Get all open shifts
    shifts = Shift.objects.filter(status="open").select_related("site")
    
    # Filter by role if staff has a primary role
    if staff.primary_role and staff.primary_role != "not_set":
        shifts = shifts.filter(role_required=staff.primary_role)
    
    # Filter by date range (next 14 days by default)
    today = datetime.now().date()
    shifts = shifts.filter(date__gte=today, date__lte=today + timedelta(days=14))
    
    # Filter by city
    city = request.GET.get('city')
    if city:
        shifts = shifts.filter(site__city__iexact=city)

    # Geo-radius filtering
    radius = staff.travel_radius_miles or 5
    # Use the site of the first shift the staff has applied to as their 'home' location (if any)
    staff_shift_request = staff.shift_requests.select_related('shift__site').first()
    staff_lat, staff_lon = None, None
    if staff_shift_request and staff_shift_request.shift.site.latitude and staff_shift_request.shift.site.longitude:
        staff_lat = staff_shift_request.shift.site.latitude
        staff_lon = staff_shift_request.shift.site.longitude
    # If staff has no venue, skip geo filtering (future: allow staff to set home location)
    if staff_lat and staff_lon:
        from geopy.distance import geodesic
        filtered_shifts = []
        for shift in shifts:
            site = shift.site
            if site.latitude and site.longitude:
                dist = geodesic((staff_lat, staff_lon), (site.latitude, site.longitude)).miles
                if dist <= radius:
                    filtered_shifts.append(shift)
        shifts = filtered_shifts
    
    # Get already applied shifts to show status
    applied_shift_ids = staff.shift_requests.values_list("shift_id", flat=True)
    
    # Add context about which shifts staff has applied to
    shifts_with_status = []
    for shift in shifts:
        applied_status = None
        if shift.id in applied_shift_ids:
            req = staff.shift_requests.get(shift_id=shift.id)
            applied_status = req.status
        
        shifts_with_status.append({
            "shift": shift,
            "applied_status": applied_status,
        })
    
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
        shift__site__in=sites,
        status="pending"
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
        if form.is_valid():
            shift = form.save(commit=False)
            shift.site = form.cleaned_data["site"]
            shift.save()
            return redirect("operator_dashboard")
    else:
        form = ShiftForm()
        # Limit site choices to operator's sites
        form.fields["site"].queryset = sites
    
    context = {
        "form": form,
        "operator": operator,
    }
    
    return render(request, "disco_app/post_shift.html", context)


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
    
    sr = get_object_or_404(ShiftRequest, id=request_id, shift__site__in=operator.sites.all())
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
    return render(request, "disco_app/manage_sites.html", {"sites": sites, "form": form, "operator": operator})
