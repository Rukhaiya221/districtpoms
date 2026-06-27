from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("citizen/register/", views.citizen_register, name="citizen_register"),
    path("citizen/login/", views.citizen_login_view, name="citizen_login"),
    path("admin-portal/register/", views.admin_register, name="admin_register"),
    path("admin-portal/login/", views.admin_login_view, name="admin_login"),
    path("electrician/register/", views.electrician_register, name="electrician_register"),
    path("electrician/login/", views.electrician_login_view, name="electrician_login"),
    path("logout/", views.logout_view, name="logout"),
    path("citizen/dashboard/", views.citizen_dashboard, name="citizen_dashboard"),
    path("citizen/report/", views.report_outage, name="report_outage"),
    path("citizen/track/<int:pk>/", views.citizen_track_outage, name="citizen_track_outage"),
    path("citizen/notifications/", views.citizen_notifications, name="citizen_notifications"),
    path("admin-portal/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-portal/outage/<int:pk>/", views.admin_outage_detail, name="admin_outage_detail"),
    path("admin-portal/electricians/", views.admin_electricians, name="admin_electricians"),
    path("admin-portal/electricians/add/", views.admin_add_electrician, name="admin_add_electrician"),
    path("admin-portal/track/<int:pk>/", views.admin_track_outage, name="admin_track_outage"),
    path("admin-portal/analytics/", views.admin_analytics, name="admin_analytics"),
    path("electrician/dashboard/", views.electrician_dashboard, name="electrician_dashboard"),
    path("electrician/outage/<int:pk>/", views.electrician_outage_detail, name="electrician_outage_detail"),
    path("api/track/<int:pk>/", views.track_location_api, name="track_location_api"),
    path("api/simulate/<int:pk>/", views.simulate_movement_api, name="simulate_movement_api"),
]
