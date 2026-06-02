from authentication.models import Staff


def get_recommended_staff_for_shift(shift):
    staff = Staff.objects.filter(
        user__is_active=True,
        user__email__isnull=False,
        wants_shift_emails=True,
    ).exclude(user__email="")

    # Basic city match
    if shift.site and shift.site.city:
        staff = staff.filter(city__iexact=shift.site.city)

    # Basic role/skills match later
    # Example future logic:
    # staff = staff.filter(skills__name__iexact=shift.role)

    return staff.distinct()
