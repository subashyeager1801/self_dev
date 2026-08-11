"""
Workout views — List, detail, generate, and complete workouts.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Exercise, WorkoutSession, WorkoutExercise
from accounts.models import UserProfile


@login_required
def workout_list_view(request):
    """List all workouts — recent sessions and today's workout."""
    profile = request.user.profile
    today = timezone.now().date()

    # Get today's workout
    todays_workout = WorkoutSession.objects.filter(
        user=request.user, date=today
    ).first()

    # Recent workouts
    recent_workouts = WorkoutSession.objects.filter(
        user=request.user
    ).exclude(date=today)[:10]

    # Workout stats
    total_sessions = WorkoutSession.objects.filter(
        user=request.user, status='completed'
    ).count()

    context = {
        'todays_workout': todays_workout,
        'recent_workouts': recent_workouts,
        'total_sessions': total_sessions,
        'profile': profile,
        'show_nav': True,
        'active_nav': 'workout',
    }
    return render(request, 'workouts/list.html', context)


@login_required
def workout_detail_view(request, session_id):
    """View and interact with a specific workout session."""
    session = get_object_or_404(WorkoutSession, id=session_id, user=request.user)
    exercises = session.exercises.select_related('exercise').all()

    context = {
        'session': session,
        'exercises': exercises,
        'show_nav': True,
        'active_nav': 'workout',
    }
    return render(request, 'workouts/detail.html', context)


@login_required
def generate_workout_view(request):
    """Generate a new AI workout. Uses rule-based logic as baseline, AI for enhancement."""
    profile = request.user.profile
    today = timezone.now().date()

    # Check if workout already exists for today
    existing = WorkoutSession.objects.filter(user=request.user, date=today).first()
    if existing:
        return redirect('workouts:detail', session_id=existing.id)

    # Determine muscle groups based on recent workouts
    recent_sessions = WorkoutSession.objects.filter(
        user=request.user,
        status='completed',
        date__gte=today - timezone.timedelta(days=7)
    ).prefetch_related('exercises__exercise')

    trained_recently = set()
    for s in recent_sessions:
        for we in s.exercises.all():
            trained_recently.add(we.exercise.muscle_group)

    # Muscle group rotation logic
    all_groups = [
        ('chest', 'triceps'),
        ('back', 'biceps'),
        ('shoulders', 'core'),
        ('quadriceps', 'hamstrings', 'glutes', 'calves'),
    ]

    # Find the least recently trained group
    best_groups = None
    for group_combo in all_groups:
        if not any(g in trained_recently for g in group_combo):
            best_groups = group_combo
            break

    if not best_groups:
        # All groups trained recently — pick first combo (chest/triceps)
        best_groups = all_groups[0]

    # Filter exercises by equipment and location
    equipment = profile.available_equipment or []
    is_home = profile.workout_location == 'home'

    exercises_qs = Exercise.objects.filter(
        muscle_group__in=best_groups
    )

    if is_home:
        exercises_qs = exercises_qs.filter(is_home_friendly=True)

    # If user has specific equipment, filter accordingly
    if equipment and 'full_gym' not in equipment and 'no_equipment' not in equipment:
        # Include bodyweight exercises + equipment-matched ones
        from django.db.models import Q
        q = Q(equipment=[])  # bodyweight
        for eq in equipment:
            q |= Q(equipment__contains=eq)
        exercises_qs = exercises_qs.filter(q)

    exercises_list = list(exercises_qs[:8])  # Max 8 exercises

    if not exercises_list:
        # Fallback: get any exercises for these muscle groups
        exercises_list = list(Exercise.objects.filter(
            muscle_group__in=best_groups
        )[:6])

    if not exercises_list:
        context = {
            'error': 'No exercises found. Please add exercises to the library.',
            'show_nav': True,
            'active_nav': 'workout',
        }
        return render(request, 'workouts/list.html', context)

    # Create workout session
    group_names = [dict(Exercise.MUSCLE_GROUP_CHOICES).get(g, g) for g in best_groups]
    title = ' + '.join(group_names)

    session = WorkoutSession.objects.create(
        user=request.user,
        title=title,
        date=today,
        target_muscle_groups=list(best_groups),
        estimated_duration_minutes=profile.daily_workout_minutes,
        difficulty_level=profile.fitness_experience,
        ai_generated=True,
        ai_notes=f"Auto-generated based on your {profile.get_fitness_goal_display()} goal. "
                 f"Focus on {title.lower()} today.",
    )

    # Determine sets/reps based on fitness goal
    goal_params = {
        'fat_loss': {'sets': 3, 'reps': '12-15', 'rest': 45},
        'muscle_gain': {'sets': 4, 'reps': '8-12', 'rest': 90},
        'athletic': {'sets': 3, 'reps': '10-12', 'rest': 60},
        'strength': {'sets': 5, 'reps': '3-5', 'rest': 120},
        'general': {'sets': 3, 'reps': '10-12', 'rest': 60},
        'maintain': {'sets': 3, 'reps': '10', 'rest': 60},
    }
    params = goal_params.get(profile.fitness_goal, goal_params['general'])

    for i, exercise in enumerate(exercises_list):
        WorkoutExercise.objects.create(
            session=session,
            exercise=exercise,
            order=i + 1,
            sets=params['sets'],
            reps=params['reps'],
            rest_seconds=params['rest'],
        )

    return redirect('workouts:detail', session_id=session.id)


@login_required
def toggle_exercise_complete(request):
    """AJAX: Toggle exercise completion status."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    exercise_id = request.POST.get('exercise_id')

    try:
        we = WorkoutExercise.objects.get(
            id=exercise_id,
            session__user=request.user
        )
        we.completed = not we.completed
        we.save()

        # Check if all exercises completed
        session = we.session
        all_done = not session.exercises.filter(completed=False).exists()
        if all_done and session.status != 'completed':
            session.status = 'completed'
            session.completed_at = timezone.now()
            session.save()

            # Update daily progress
            from dashboard.models import DailyProgress
            daily, _ = DailyProgress.objects.get_or_create(
                user=request.user, date=timezone.now().date()
            )
            daily.workout_completed = True
            daily.workout_duration_minutes = session.estimated_duration_minutes
            daily.calculate_score()
            daily.save()

        return JsonResponse({
            'status': 'ok',
            'completed': we.completed,
            'session_completion': session.completion_percentage,
            'all_done': all_done,
        })
    except WorkoutExercise.DoesNotExist:
        return JsonResponse({'error': 'Exercise not found'}, status=404)


@login_required
def rate_workout(request):
    """AJAX: Rate a completed workout."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    session_id = request.POST.get('session_id')
    rating = int(request.POST.get('rating', 3))
    notes = request.POST.get('notes', '')

    try:
        session = WorkoutSession.objects.get(id=session_id, user=request.user)
        session.user_rating = rating
        session.user_notes = notes
        session.save()
        return JsonResponse({'status': 'ok'})
    except WorkoutSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)
