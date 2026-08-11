"""
Mind views — 1-10 Mental Check-In, Journaling with AI reflection, and emotional trends.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import MoodLog, JournalEntry
from ai_engine.mind_ai import analyze_journal_entry


@login_required
def mind_dashboard_view(request):
    """Main Mind & Mental Development page."""
    today = timezone.now().date()
    today_checkin, _ = MoodLog.objects.get_or_create(user=request.user, date=today)

    recent_journals = JournalEntry.objects.filter(user=request.user)[:10]
    recent_checkins = MoodLog.objects.filter(user=request.user)[:7]

    # Calculate average focus and stress over past week
    avg_focus = sum(c.focus for c in recent_checkins) / len(recent_checkins) if recent_checkins else 7.0
    avg_stress = sum(c.stress for c in recent_checkins) / len(recent_checkins) if recent_checkins else 4.0

    context = {
        'today_checkin': today_checkin,
        'mind_score': today_checkin.mind_score,
        'recent_journals': recent_journals,
        'avg_focus': round(avg_focus, 1),
        'avg_stress': round(avg_stress, 1),
        'show_nav': True,
        'active_nav': 'mind',
    }
    return render(request, 'mind/index.html', context)


@login_required
def update_checkin_api(request):
    """AJAX endpoint to update 1-10 check-in values."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    today = timezone.now().date()
    checkin, _ = MoodLog.objects.get_or_create(user=request.user, date=today)

    field = request.POST.get('field')
    value = request.POST.get('value')

    allowed_fields = ['mood', 'energy', 'focus', 'stress', 'motivation', 'sleep_quality', 'mental_clarity']
    if field not in allowed_fields:
        return JsonResponse({'error': 'Invalid metric'}, status=400)

    try:
        val_int = max(1, min(int(value), 10))
        setattr(checkin, field, val_int)
        checkin.save()
        return JsonResponse({'status': 'ok', 'score': checkin.mind_score, 'field': field, 'value': val_int})
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid number'}, status=400)


@login_required
def create_journal_api(request):
    """Save a daily journal entry and generate AI supportive reflection."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()

    if not content:
        return JsonResponse({'error': 'Content cannot be empty'}, status=400)

    today = timezone.now().date()
    checkin, _ = MoodLog.objects.get_or_create(user=request.user, date=today)

    mood_dict = {
        'mood': checkin.mood,
        'energy': checkin.energy,
        'focus': checkin.focus,
        'stress': checkin.stress,
        'motivation': checkin.motivation,
    }

    # Analyze via AI engine
    ai_result = analyze_journal_entry(content, mood_dict)

    entry = JournalEntry.objects.create(
        user=request.user,
        date=today,
        title=title or f"Reflection for {today.strftime('%b %d')}",
        content=content,
        ai_reflection=ai_result.get('reflection', ''),
        detected_patterns=ai_result.get('detected_patterns', []),
        actionable_advice=ai_result.get('actionable_advice', '')
    )

    return JsonResponse({
        'status': 'ok',
        'id': entry.id,
        'ai_reflection': entry.ai_reflection,
        'actionable_advice': entry.actionable_advice,
        'patterns': entry.detected_patterns
    })
