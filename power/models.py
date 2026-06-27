from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Government Admin"),
        ("citizen", "Citizen"),
        ("electrician", "Electrician"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="citizen")
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)

    def is_gov_admin(self):
        return self.role == "admin"

    def is_citizen(self):
        return self.role == "citizen"

    def is_electrician(self):
        return self.role == "electrician"


class Electrician(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="electrician_profile"
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    employee_id = models.CharField(max_length=20, unique=True)
    is_available = models.BooleanField(default=True)
    current_latitude = models.FloatField(default=28.6139)
    current_longitude = models.FloatField(default=77.2090)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.employee_id})"


class OutageReport(models.Model):
    STATUS_CHOICES = [
        ("reported", "Reported"),
        ("assigned", "Electrician Assigned"),
        ("en_route", "Electrician En Route"),
        ("in_progress", "Work In Progress"),
        ("resolved", "Power Restored"),
        ("cancelled", "Cancelled"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("emergency", "Emergency"),
    ]

    citizen = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="outage_reports"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    latitude = models.FloatField(default=28.6139)
    longitude = models.FloatField(default=77.2090)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="reported")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    assigned_electrician = models.ForeignKey(
        Electrician,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_outages",
    )
    estimated_restoration = models.DateTimeField(null=True, blank=True)
    is_escalated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    outage = models.ForeignKey(
        OutageReport, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notification for {self.user.username}"


class LocationUpdate(models.Model):
    electrician = models.ForeignKey(
        Electrician, on_delete=models.CASCADE, related_name="location_history"
    )
    outage = models.ForeignKey(
        OutageReport, on_delete=models.CASCADE, related_name="location_updates", null=True, blank=True
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
