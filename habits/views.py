"""
Habits views — Daily Habit tracking, streaks, and compassionate restart coaching.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import DisciplineHabit, DisciplineHabitLog


@login_required
def habits_dashboard_view(request):
    """Main Habits & Discipline page with streaks and restart coaching."""
    today = timezone.now().date()
    habits = DisciplineHabit.objects.filter(user=request.user)

    habit_items = []
    completed_today_count = 0

    for habit in habits:
        log, _ = DisciplineHabitLog.objects.get_or_create(habit=habit, date=today)
        if log.completed:
            completed_today_count += 1
        habit_items.append({'habit': habit, 'log': log})

    # AI compassionate restart message if some habits were missed
    total_habits = habits.count()
    adherence_pct = int((completed_today_count / total_habits) * 100) if total_habits > 0 else 100

    context = {
        'habit_items': habit_items,
        'completed_today_count': completed_today_count,
        'total_habits': total_habits,
        'adherence_pct': adherence_pct,
        'show_nav': True,
        'active_nav': 'habits',
    }
    return render(request, 'habits/index.html', context)


@login_required
def toggle_habit_log_api(request):
    """Toggle completion status of a habit for today and update streak count."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    habit_id = request.POST.get('habit_id')
    today = timezone.now().date()

    try:
        habit = DisciplineHabit.objects.get(id=habit_id, user=request.user)
        log, _ = DisciplineHabitLog.objects.get_or_create(habit=habit, date=today)
        log.completed = not log.completed
        log.save()

        # Update streak
        if log.completed:
            habit.current_streak += 1
            if habit.current_streak > habit.best_streak:
                habit.best_streak = habit.current_streak
        else:
            habit.current_streak = max(0, habit.current_streak - 1)
        habit.save()

        return JsonResponse({
            'status': 'ok',
            'completed': log.completed,
            'current_streak': habit.current_streak,
            'best_streak': habit.best_streak,
        })
    except DisciplineHabit.DoesNotExist:
        return JsonResponse({'error': 'Habit not found'}, status=404)


@login_required
def create_habit_api(request):
    """Create a new custom discipline habit."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    name = request.POST.get('name', '').strip()
    icon = request.POST.get('icon', '🎯')
    frequency = request.POST.get('frequency', 'daily')
    target = request.POST.get('target', '')

    if not name:
        return JsonResponse({'error': 'Name required'}, status=400)

    habit = DisciplineHabit.objects.create(
        user=request.user,
        name=name,
        icon=icon,
        frequency=frequency,
        target_description=target
    )

    return JsonResponse({'status': 'ok', 'id': habit.id})
