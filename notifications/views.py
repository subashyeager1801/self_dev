"""
Notifications views — Reminder settings and in-app alerts.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import NotificationPreference, InAppNotification


@login_required
def notification_center_view(request):
    """Notification center & reminder preferences."""
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
    notifications = InAppNotification.objects.filter(user=request.user)[:20]

    context = {
        'prefs': prefs,
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
        'show_nav': True,
        'active_nav': 'notifications',
    }
    return render(request, 'notifications/index.html', context)


@login_required
def update_preferences_api(request):
    """Update toggleable reminder preferences."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
    prefs.workout_reminder = request.POST.get('workout_reminder') == 'true'
    prefs.water_reminder = request.POST.get('water_reminder') == 'true'
    prefs.meal_reminder = request.POST.get('meal_reminder') == 'true'
    prefs.learning_reminder = request.POST.get('learning_reminder') == 'true'
    prefs.habit_reminder = request.POST.get('habit_reminder') == 'true'
    prefs.sleep_reminder = request.POST.get('sleep_reminder') == 'true'
    prefs.reflection_reminder = request.POST.get('reflection_reminder') == 'true'
    prefs.save()

    return JsonResponse({'status': 'ok'})


@login_required
def mark_read_api(request):
    """Mark all notifications as read."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    InAppNotification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'ok'})


@login_required
def trigger_test_notification_api(request):
    """Generate a contextual AI coach check-in notification for immediate demonstration."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    notif_type = request.POST.get('type', 'coach')
    
    type_messages = {
        'coach': ("🤖 AI Coach Daily Check-In", "Remember your top priority for today: stay consistent and hit your daily targets!"),
        'workout': ("💪 Workout Prompt", "Time for your daily training session! Keep your streak alive."),
        'water': ("💧 Hydration Check", "Have you logged your water intake today? Aim for 3.5L."),
        'habit': ("🎯 Habit Streak Check", "Check off your daily habits before wrapping up your day."),
        'learn': ("📚 Learning Session Reminder", "Dedicate 45 minutes to your active curriculum track today."),
    }
    
    title, msg = type_messages.get(notif_type, type_messages['coach'])

    notif = InAppNotification.objects.create(
        user=request.user,
        title=title,
        message=msg,
        notification_type=notif_type,
        action_url='/dashboard/'
    )

    return JsonResponse({'status': 'ok', 'title': notif.title, 'message': notif.message})


@login_required
def manage_single_notification_api(request):
    """Mark single notification as read or delete."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    notif_id = request.POST.get('notification_id')
    action = request.POST.get('action', 'read')

    try:
        notif = InAppNotification.objects.get(id=notif_id, user=request.user)
        if action == 'delete':
            notif.delete()
        else:
            notif.is_read = True
            notif.save()
        return JsonResponse({'status': 'ok'})
    except InAppNotification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)
