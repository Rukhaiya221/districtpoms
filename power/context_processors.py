def notifications_context(request):
    if request.user.is_authenticated and request.user.role == "citizen":
        from .models import Notification
        return {
            "unread_count": Notification.objects.filter(
                user=request.user, is_read=False
            ).count()
        }
    return {"unread_count": 0}
