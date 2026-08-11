"""
Growth views — Cascading Long-Term Goals Hierarchy (10-Year to Daily) and Habit Milestones.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from .models import GrowthCategory, Goal, GoalProgress, GoalHierarchy


def _ensure_categories(user):
    """Create preset categories if user has none."""
    if not GrowthCategory.objects.filter(user=user).exists():
        for slug, name, icon in GrowthCategory.PRESET_CATEGORIES:
            GrowthCategory.objects.create(user=user, name=name, icon=icon, is_preset=True)


@login_required
def growth_dashboard_view(request):
    """Self-development & long-term goals hierarchy dashboard."""
    _ensure_categories(request.user)

    categories = GrowthCategory.objects.filter(user=request.user)
    goals = Goal.objects.filter(user=request.user, is_active=True)
    hierarchies = GoalHierarchy.objects.filter(user=request.user)

    context = {
        'categories': categories,
        'goals': goals,
        'hierarchies': hierarchies,
        'total_goals': goals.count(),
        'show_nav': True,
        'active_nav': 'goals',
    }
    return render(request, 'growth/dashboard.html', context)


@login_required
def create_hierarchy_api(request):
    """Create a 10-year cascading vision hierarchy."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    ten_year = request.POST.get('ten_year_vision', '').strip()
    yearly = request.POST.get('yearly_goal', '').strip()
    monthly = request.POST.get('monthly_goal', '').strip()
    weekly = request.POST.get('weekly_goal', '').strip()
    daily = request.POST.get('daily_action', '').strip()

    if not ten_year or not yearly:
        return JsonResponse({'error': 'Vision and Yearly goal required'}, status=400)

    hierarchy = GoalHierarchy.objects.create(
        user=request.user,
        ten_year_vision=ten_year,
        yearly_goal=yearly,
        monthly_goal=monthly,
        weekly_goal=weekly,
        daily_action=daily
    )

    return JsonResponse({'status': 'ok', 'id': hierarchy.id})


@login_required
def manage_goals(request):
    """AJAX: Create, update, or delete goals."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    action = request.POST.get('action')

    if action == 'create':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category_id')
        goal_type = request.POST.get('goal_type', 'long_term')
        target_value = float(request.POST.get('target_value', 100))
        unit = request.POST.get('unit', '')

        if not title:
            return JsonResponse({'error': 'Title required'}, status=400)

        category = None
        if category_id:
            try:
                category = GrowthCategory.objects.get(id=category_id, user=request.user)
            except GrowthCategory.DoesNotExist:
                pass

        Goal.objects.create(
            user=request.user,
            category=category,
            title=title,
            goal_type=goal_type,
            target_value=target_value,
            unit=unit,
        )
        return JsonResponse({'status': 'ok'})

    elif action == 'update_progress':
        goal_id = request.POST.get('goal_id')
        value = float(request.POST.get('value', 0))

        try:
            goal = Goal.objects.get(id=goal_id, user=request.user)
            goal.current_value = min(goal.current_value + value, goal.target_value)
            goal.save()

            return JsonResponse({
                'status': 'ok',
                'progress': goal.progress_percentage,
                'current': goal.current_value,
                'completed': goal.is_completed,
            })
        except Goal.DoesNotExist:
            return JsonResponse({'error': 'Goal not found'}, status=404)

    return JsonResponse({'error': 'Invalid action'}, status=400)
