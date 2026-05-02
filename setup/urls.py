from django.contrib import admin
from django.urls import path
from authentication import views as auth_views
from disco_app import views as disco_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", disco_views.home, name="home"),
    path("register/", auth_views.register, name="register"),
    path("login/", auth_views.login, name="login"),
    path("logout/", auth_views.logout, name="logout"),
    path("availability/", auth_views.manage_availability, name="manage_availability"),
    path("availability/<int:availability_id>/delete/", auth_views.delete_availability, name="delete_availability"),
    # Staff views
    path("dashboard/", disco_views.staff_dashboard, name="staff_dashboard"),
    path("shifts/", disco_views.browse_shifts, name="browse_shifts"),
    path("shifts/<int:shift_id>/apply/", disco_views.apply_for_shift, name="apply_for_shift"),
    # Operator views
    path("operator/", disco_views.operator_dashboard, name="operator_dashboard"),
    path("operator/shifts/post/", disco_views.post_shift, name="post_shift"),
    path("operator/shifts/<int:shift_id>/requests/", disco_views.manage_shift_requests, name="manage_shift_requests"),
    path("operator/requests/<int:request_id>/respond/", disco_views.respond_to_request, name="respond_to_request"),
    path("operator/sites/", disco_views.manage_sites, name="manage_sites"),
]
