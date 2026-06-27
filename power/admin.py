from django.contrib import admin

from .models import Electrician, LocationUpdate, Notification, OutageReport, User

admin.site.register(User)
admin.site.register(Electrician)
admin.site.register(OutageReport)
admin.site.register(Notification)
admin.site.register(LocationUpdate)
