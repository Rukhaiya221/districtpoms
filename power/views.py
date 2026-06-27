from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AdminRegistrationForm,
    AssignElectricianForm,
    CitizenRegistrationForm,
    ElectricianForm,
    ElectricianRegistrationForm,
    OutageReportForm,
    UpdateStatusForm,
)
from .models import Electrician, LocationUpdate, Notification, OutageReport, User


def is_admin(user):
    return user.is_authenticated and user.role == "admin"


def is_citizen(user):
    return user.is_authenticated and user.role == "citizen"


def home(request):
    if request.user.is_authenticated:
        if request.user.role == "admin":
            return redirect("admin_dashboard")
        return redirect("citizen_dashboard")
    return render(request, "power/home.html")


def citizen_register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please log in.")
            return redirect("citizen_login")
    else:
        form = CitizenRegistrationForm()
    return render(request, "power/auth/register_citizen.html", {"form": form})


def admin_register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Admin registration successful! Please log in.")
            return redirect("admin_login")
    else:
        form = AdminRegistrationForm()
    return render(request, "power/auth/register_admin.html", {"form": form})


def citizen_login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user and user.role == "citizen":
            login(request, user)
            return redirect("citizen_dashboard")
        messages.error(request, "Invalid credentials or not a citizen account.")
    return render(request, "power/auth/login_citizen.html")


def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user and user.role == "admin":
            login(request, user)
            return redirect("admin_dashboard")
        messages.error(request, "Invalid credentials or not an admin account.")
    return render(request, "power/auth/login_admin.html")


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("home")


def electrician_register(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = ElectricianRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Electrician registration successful! Please log in.")
            return redirect("electrician_login")
    else:
        form = ElectricianRegistrationForm()
    return render(request, "power/auth/register_electrician.html", {"form": form})


def electrician_login_view(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user and user.role == "electrician":
            login(request, user)
            return redirect("electrician_dashboard")
        messages.error(request, "Invalid credentials or not an electrician account.")
    return render(request, "power/auth/login_electrician.html")


@login_required
def electrician_dashboard(request):
    if not request.user.is_authenticated or request.user.role != "electrician":
        messages.error(request, "Unauthorized")
        return redirect("home")
    electrician = getattr(request.user, "electrician_profile", None)
    if not electrician:
        messages.warning(request, "No electrician profile found.")
        return redirect("home")
    assigned = OutageReport.objects.filter(assigned_electrician=electrician)
    return render(request, "power/electrician/dashboard.html", {"outages": assigned, "electrician": electrician})


@login_required
def electrician_outage_detail(request, pk):
    if not request.user.role == "electrician":
        return redirect("home")
    electrician = getattr(request.user, "electrician_profile", None)
    outage = get_object_or_404(OutageReport.objects.select_related("citizen", "assigned_electrician"), pk=pk)
    if outage.assigned_electrician != electrician:
        messages.error(request, "You are not assigned to this outage.")
        return redirect("electrician_dashboard")

    if request.method == "POST":
        # send notification to all admins about work status/message
        message = request.POST.get("message", "")
        if message:
            admins = User.objects.filter(role="admin")
            for admin in admins:
                Notification.objects.create(user=admin, outage=outage, message=f"From electrician {electrician.name}: {message}")
            messages.success(request, "Status sent to admins.")
            return redirect("electrician_outage_detail", pk=pk)

    return render(request, "power/electrician/outage_detail.html", {"outage": outage, "electrician": electrician})


@login_required
@user_passes_test(is_citizen)
def citizen_dashboard(request):
    reports = OutageReport.objects.filter(citizen=request.user)
    return render(
        request,
        "power/citizen/dashboard.html",
        {"reports": reports},
    )


@login_required
@user_passes_test(is_citizen)
def report_outage(request):
    if request.method == "POST":
        form = OutageReportForm(request.POST)
        if form.is_valid():
            outage = form.save(commit=False)
            outage.citizen = request.user
            if outage.priority == "emergency":
                outage.is_escalated = True
            outage.save()
            Notification.objects.create(
                user=request.user,
                outage=outage,
                message=f"Your outage report '{outage.title}' has been submitted successfully.",
            )
            messages.success(request, "Outage reported successfully!")
            return redirect("citizen_dashboard")
    else:
        form = OutageReportForm()
    return render(request, "power/citizen/report_outage.html", {"form": form})


@login_required
@user_passes_test(is_citizen)
def citizen_track_outage(request, pk):
    outage = get_object_or_404(OutageReport, pk=pk, citizen=request.user)
    return render(request, "power/citizen/track_outage.html", {"outage": outage})


@login_required
@user_passes_test(is_citizen)
def citizen_notifications(request):
    notifications = Notification.objects.filter(user=request.user)
    notifications.filter(is_read=False).update(is_read=True)
    return render(
        request, "power/citizen/notifications.html", {"notifications": notifications}
    )


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    outages = OutageReport.objects.select_related("citizen", "assigned_electrician").all()
    stats = {
        "total": outages.count(),
        "active": outages.exclude(status__in=["resolved", "cancelled"]).count(),
        "resolved": outages.filter(status="resolved").count(),
        "emergency": outages.filter(is_escalated=True, status__in=["reported", "assigned", "en_route", "in_progress"]).count(),
    }
    return render(
        request,
        "power/admin/dashboard.html",
        {"outages": outages, "stats": stats},
    )


@login_required
@user_passes_test(is_admin)
def admin_outage_detail(request, pk):
    outage = get_object_or_404(
        OutageReport.objects.select_related("citizen", "assigned_electrician"), pk=pk
    )
    assign_form = AssignElectricianForm()
    status_form = UpdateStatusForm(initial={"status": outage.status})
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "assign":
            assign_form = AssignElectricianForm(request.POST)
            if assign_form.is_valid():
                electrician = assign_form.cleaned_data["electrician"]
                outage.assigned_electrician = electrician
                outage.status = "assigned"
                outage.estimated_restoration = assign_form.cleaned_data.get("estimated_restoration")
                outage.save()
                electrician.is_available = False
                electrician.save()
                _notify_citizen(
                    outage,
                    f"An electrician ({electrician.name}) has been assigned to your outage. "
                    f"Contact: {electrician.phone}",
                )
                messages.success(request, f"Assigned {electrician.name} to this outage.")
                return redirect("admin_outage_detail", pk=pk)
        elif action == "update_status":
            status_form = UpdateStatusForm(request.POST)
            if status_form.is_valid():
                old_status = outage.status
                new_status = status_form.cleaned_data["status"]
                outage.status = new_status
                if status_form.cleaned_data.get("estimated_restoration"):
                    outage.estimated_restoration = status_form.cleaned_data["estimated_restoration"]
                if new_status == "resolved":
                    outage.resolved_at = timezone.now()
                    if outage.assigned_electrician:
                        outage.assigned_electrician.is_available = True
                        outage.assigned_electrician.save()
                elif new_status == "en_route" and old_status != "en_route":
                    _start_tracking_simulation(outage)
                outage.save()
                _notify_citizen(
                    outage,
                    f"Status update for '{outage.title}': {outage.get_status_display()}"
                    + (f". ETA: {outage.estimated_restoration.strftime('%b %d, %Y %H:%M')}" if outage.estimated_restoration else ""),
                )
                messages.success(request, "Status updated successfully.")
                return redirect("admin_outage_detail", pk=pk)
        elif action == "escalate":
            outage.is_escalated = True
            outage.priority = "emergency"
            outage.save()
            _notify_citizen(outage, f"Your outage '{outage.title}' has been escalated to emergency priority.")
            messages.warning(request, "Outage escalated to emergency.")
            return redirect("admin_outage_detail", pk=pk)

    return render(
        request,
        "power/admin/outage_detail.html",
        {
            "outage": outage,
            "assign_form": assign_form,
            "status_form": status_form,
        },
    )


@login_required
@user_passes_test(is_admin)
def admin_electricians(request):
    electricians = Electrician.objects.all()
    return render(
        request, "power/admin/electricians.html", {"electricians": electricians}
    )


@login_required
@user_passes_test(is_admin)
def admin_add_electrician(request):
    if request.method == "POST":
        form = ElectricianForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Electrician added successfully.")
            return redirect("admin_electricians")
    else:
        form = ElectricianForm()
    return render(request, "power/admin/add_electrician.html", {"form": form})


@login_required
@user_passes_test(is_admin)
def admin_track_outage(request, pk):
    outage = get_object_or_404(
        OutageReport.objects.select_related("citizen", "assigned_electrician"), pk=pk
    )
    return render(request, "power/admin/track_outage.html", {"outage": outage})


@login_required
@user_passes_test(is_admin)
def admin_analytics(request):
    outages = OutageReport.objects.all()
    status_breakdown = (
        outages.values("status").annotate(count=Count("id")).order_by("-count")
    )
    priority_breakdown = (
        outages.values("priority").annotate(count=Count("id")).order_by("-count")
    )
    resolved_outages = outages.filter(status="resolved", resolved_at__isnull=False)
    avg_resolution = None
    if resolved_outages.exists():
        total_hours = sum(
            (o.resolved_at - o.created_at).total_seconds() / 3600
            for o in resolved_outages
        )
        avg_resolution = round(total_hours / resolved_outages.count(), 1)

    recent = outages.order_by("-created_at")[:10]
    return render(
        request,
        "power/admin/analytics.html",
        {
            "total_outages": outages.count(),
            "resolved_count": outages.filter(status="resolved").count(),
            "active_count": outages.exclude(status__in=["resolved", "cancelled"]).count(),
            "status_breakdown": status_breakdown,
            "priority_breakdown": priority_breakdown,
            "avg_resolution_hours": avg_resolution,
            "recent_outages": recent,
        },
    )


@login_required
def track_location_api(request, pk):
    outage = get_object_or_404(OutageReport, pk=pk)
    if request.user.role == "citizen" and outage.citizen != request.user:
        return JsonResponse({"error": "Unauthorized"}, status=403)
    if not outage.assigned_electrician:
        return JsonResponse({"error": "No electrician assigned"}, status=404)

    electrician = outage.assigned_electrician
    return JsonResponse(
        {
            "electrician_name": electrician.name,
            "electrician_phone": electrician.phone,
            "latitude": electrician.current_latitude,
            "longitude": electrician.current_longitude,
            "outage_latitude": outage.latitude,
            "outage_longitude": outage.longitude,
            "status": outage.status,
        }
    )


@login_required
@user_passes_test(is_admin)
@require_POST
def simulate_movement_api(request, pk):
    outage = get_object_or_404(OutageReport, pk=pk)
    if not outage.assigned_electrician:
        return JsonResponse({"error": "No electrician assigned"}, status=404)

    electrician = outage.assigned_electrician
    target_lat = float(request.POST.get("target_lat", outage.latitude))
    target_lng = float(request.POST.get("target_lng", outage.longitude))
    step = 0.002

    lat_diff = target_lat - electrician.current_latitude
    lng_diff = target_lng - electrician.current_longitude
    distance = (lat_diff**2 + lng_diff**2) ** 0.5

    if distance < step:
        electrician.current_latitude = target_lat
        electrician.current_longitude = target_lng
    else:
        electrician.current_latitude += (lat_diff / distance) * step
        electrician.current_longitude += (lng_diff / distance) * step

    electrician.save()
    LocationUpdate.objects.create(
        electrician=electrician,
        outage=outage,
        latitude=electrician.current_latitude,
        longitude=electrician.current_longitude,
    )

    arrived = distance < step
    if arrived and outage.status == "en_route":
        outage.status = "in_progress"
        outage.save()
        _notify_citizen(outage, f"Electrician {electrician.name} has arrived at your location.")

    return JsonResponse(
        {
            "latitude": electrician.current_latitude,
            "longitude": electrician.current_longitude,
            "arrived": arrived,
            "status": outage.status,
        }
    )


def _notify_citizen(outage, message):
    Notification.objects.create(user=outage.citizen, outage=outage, message=message)


def _start_tracking_simulation(outage):
    if outage.assigned_electrician:
        LocationUpdate.objects.create(
            electrician=outage.assigned_electrician,
            outage=outage,
            latitude=outage.assigned_electrician.current_latitude,
            longitude=outage.assigned_electrician.current_longitude,
        )
