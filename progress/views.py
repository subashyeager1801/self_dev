"""
Progress views — Analytics dashboard with charts, weekly AI review, and monthly growth report.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
from .models import WeightHistory
from dashboard.models import DailyProgress
from workouts.models import WorkoutSession
from coach.models import AIRecommendation
from ai_engine.progress_ai import generate_weekly_report


@login_required
def progress_dashboard_view(request):
    """Main progress analytics page."""
    profile = request.user.profile
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    seven_days_ago = today - timedelta(days=7)

    # Weight history
    weight_data = WeightHistory.objects.filter(
        user=request.user, date__gte=thirty_days_ago
    ).order_by('date')

    weight_labels = [w.date.strftime('%b %d') for w in weight_data]
    weight_values = [w.weight_kg for w in weight_data]

    # Daily progress for the last 7 days
    daily_data = DailyProgress.objects.filter(
        user=request.user, date__gte=seven_days_ago
    ).order_by('date')

    daily_labels = [d.date.strftime('%a') for d in daily_data]
    daily_scores = [d.daily_score for d in daily_data]
    daily_protein = [d.protein_consumed for d in daily_data]
    daily_water = [d.water_liters for d in daily_data]
    daily_sleep = [d.sleep_hours for d in daily_data]

    # Workout stats
    workouts_this_week = WorkoutSession.objects.filter(
        user=request.user,
        date__gte=seven_days_ago,
        status='completed'
    ).count()

    total_workouts = WorkoutSession.objects.filter(
        user=request.user,
        status='completed'
    ).count()

    # Weekly averages
    avg_score = sum(daily_scores) / len(daily_scores) if daily_scores else 0
    avg_sleep = sum(daily_sleep) / len(daily_sleep) if daily_sleep else 0
    avg_water = sum(daily_water) / len(daily_water) if daily_water else 0

    # Get or generate Weekly AI Life Review
    weekly_review = AIRecommendation.objects.filter(
        user=request.user, rec_type='weekly_report'
    ).first()

    if not weekly_review:
        weekly_payload = {
            'workouts_completed': workouts_this_week,
            'workout_target': profile.workout_days_per_week,
            'avg_daily_score': int(avg_score),
            'avg_sleep': round(avg_sleep, 1),
            'avg_water': round(avg_water, 1),
            'protein_target': profile.protein_target_grams or 100,
        }
        report_text = generate_weekly_report(weekly_payload)
        weekly_review = AIRecommendation.objects.create(
            user=request.user,
            rec_type='weekly_report',
            content=report_text,
            date=today
        )

    context = {
        'profile': profile,
        'weight_labels': json.dumps(weight_labels),
        'weight_values': json.dumps(weight_values),
        'daily_labels': json.dumps(daily_labels),
        'daily_scores': json.dumps(daily_scores),
        'daily_protein': json.dumps(daily_protein),
        'daily_water': json.dumps(daily_water),
        'daily_sleep': json.dumps(daily_sleep),
        'workouts_this_week': workouts_this_week,
        'total_workouts': total_workouts,
        'workout_target': profile.workout_days_per_week,
        'avg_score': round(avg_score),
        'avg_sleep': round(avg_sleep, 1),
        'avg_water': round(avg_water, 1),
        'weekly_review': weekly_review,
        'show_nav': True,
        'active_nav': 'progress',
    }
    return render(request, 'progress/dashboard.html', context)


@login_required
def log_weight_view(request):
    """AJAX: Log a new weight entry."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    weight = float(request.POST.get('weight', 0))
    if weight <= 0:
        return JsonResponse({'error': 'Invalid weight'}, status=400)

    today = timezone.now().date()
    entry, created = WeightHistory.objects.update_or_create(
        user=request.user, date=today,
        defaults={'weight_kg': weight}
    )

    profile = request.user.profile
    profile.weight_kg = weight
    profile.save()

    return JsonResponse({'status': 'ok', 'weight': weight, 'date': str(today)})
