"""
Context processor to inject unread notifications count across all templates.
"""
from .models import InAppNotification


def unread_notifications_processor(request):
    """Adds unread_notifications_count to template context."""
    if request.user.is_authenticated:
        count = InAppNotification.objects.filter(user=request.user, is_read=False).count()
        return {'unread_notifications_count': count}
    return {'unread_notifications_count': 0}
