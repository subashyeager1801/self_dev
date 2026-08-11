"""
Notifications utility functions.
"""
from .models import InAppNotification, NotificationPreference


def send_in_app_notification(user, title: str, message: str, notification_type: str = 'coach', action_url: str = '') -> InAppNotification:
    """Helper to dispatch an in-app notification to a user."""
    # Check preferences if relevant
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)
    
    if notification_type == 'workout' and not prefs.workout_reminder:
        return None
    if notification_type == 'habit' and not prefs.habit_reminder:
        return None
    if notification_type == 'learn' and not prefs.learning_reminder:
        return None

    return InAppNotification.objects.create(
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
        is_read=False
    )
