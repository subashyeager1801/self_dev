"""
Dashboard views — Holistic Multi-Pillar Growth Score, Explainability Feed, Daily Task Matrix, and Evening Reflection.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from .models import DailyProgress, Habit, HabitLog, DailyGrowthScore, DailyTask, EveningReflection
from accounts.models import UserProfile
from mind.models import MoodLog
from learning.models import LearningGoal, LearningSession
from career.models import CareerProfile, CareerMilestone
from workouts.models import WorkoutSession


@login_required
def home_view(request):
    """Main dashboard / holistic life growth center."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if not profile.profile_completed:
        return redirect('accounts:profile_setup')

    today = timezone.now().date()
    daily, _ = DailyProgress.objects.get_or_create(user=request.user, date=today)
    daily.calculate_score()
    daily.save()

    # Holistic Multi-pillar growth score calculation
    growth_score, _ = DailyGrowthScore.objects.get_or_create(user=request.user, date=today)

    # 1. Body score (Workouts + Protein + Hydration + Sleep)
    body_score = int((
        (25 if daily.workout_completed else 10) +
        (min(daily.protein_consumed / max(profile.estimated_protein_grams or 100, 1), 1.0) * 25) +
        (min(daily.water_liters / max(profile.water_target_liters, 1), 1.0) * 25) +
        (min(daily.sleep_hours / max(profile.sleep_target_hours, 1), 1.0) * 25)
    ))
    growth_score.body_score = min(body_score, 100)

    # 2. Mind score from MoodLog
    mood_checkin = MoodLog.objects.filter(user=request.user, date=today).first()
    growth_score.mind_score = mood_checkin.mind_score if mood_checkin else 75

    # 3. Learning score (hours + study sessions)
    learning_sessions_today = LearningSession.objects.filter(goal__user=request.user, date=today).count()
    growth_score.learning_score = min(70 + (learning_sessions_today * 15), 100)

    # 4. Career score (milestones + readiness)
    career_profile = CareerProfile.objects.filter(user=request.user).first()
    growth_score.career_score = career_profile.interview_readiness_score if career_profile else 65

    # 5. Discipline & Habits score
    habits = Habit.objects.filter(user=request.user, is_active=True)
    done_habits = HabitLog.objects.filter(habit__user=request.user, date=today, completed=True).count()
    total_habits = habits.count()
    habit_pct = int((done_habits / total_habits) * 100) if total_habits > 0 else 80
    growth_score.habits_score = habit_pct
    growth_score.discipline_score = min(int((growth_score.body_score + habit_pct) / 2), 100)

    # Overall weighted score
    growth_score.compute_overall()

    # Generate why score changed explanation
    if not growth_score.why_changed_explanation:
        explanations = []
        if daily.workout_completed:
            explanations.append("💪 Your Body score rose because today's training session was completed.")
        else:
            explanations.append("💪 Body score has potential upside: complete today's scheduled workout.")
        if done_habits >= 3:
            explanations.append("🎯 Habits & Discipline are strong with 3+ streaks maintained.")
        if growth_score.mind_score >= 80:
            explanations.append("🧠 Mental clarity & focus are above baseline today.")
        growth_score.why_changed_explanation = " · ".join(explanations)
        growth_score.save()

    # Daily Tasks
    daily_tasks = DailyTask.objects.filter(user=request.user, date=today)

    # Evening reflection
    reflection = EveningReflection.objects.filter(user=request.user, date=today).first()

    # Time greeting
    hour = timezone.now().hour
    if hour < 12:
        greeting = 'Good Morning'
    elif hour < 17:
        greeting = 'Good Afternoon'
    elif hour < 21:
        greeting = 'Good Evening'
    else:
        greeting = 'Good Night'

    context = {
        'profile': profile,
        'daily': daily,
        'growth_score': growth_score,
        'daily_tasks': daily_tasks,
        'reflection': reflection,
        'greeting': greeting,
        'today': today,
        'show_nav': True,
        'active_nav': 'home',
        'protein_target': profile.protein_target_grams or profile.estimated_protein_grams or 100,
        'water_target': profile.water_target_liters or 3.0,
        'sleep_target': profile.sleep_target_hours or 7.5,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def manage_tasks_api(request):
    """Create or toggle prioritized daily tasks."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    action = request.POST.get('action')
    today = timezone.now().date()

    if action == 'create':
        title = request.POST.get('title', '').strip()
        priority = request.POST.get('priority', 'medium')
        category = request.POST.get('category', 'General')
        if title:
            DailyTask.objects.create(user=request.user, date=today, title=title, priority=priority, category=category)
            return JsonResponse({'status': 'ok'})

    elif action == 'toggle':
        task_id = request.POST.get('task_id')
        try:
            task = DailyTask.objects.get(id=task_id, user=request.user)
            task.completed = not task.completed
            task.save()
            return JsonResponse({'status': 'ok', 'completed': task.completed})
        except DailyTask.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)

    return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
def save_reflection_api(request):
    """Save the evening reflection answers."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    well = request.POST.get('what_went_well', '').strip()
    better = request.POST.get('what_could_be_better', '').strip()
    tomorrow = request.POST.get('one_improvement_tomorrow', '').strip()

    today = timezone.now().date()
    reflection, _ = EveningReflection.objects.update_or_create(
        user=request.user, date=today,
        defaults={
            'what_went_well': well,
            'what_could_be_better': better,
            'one_improvement_tomorrow': tomorrow,
            'ai_summary': f"Today's reflection logged. Tomorrow's focal point: {tomorrow}"
        }
    )
    return JsonResponse({'status': 'ok'})
