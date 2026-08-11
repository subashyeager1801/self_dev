"""
Learning views — Roadmaps for DSA, AI/ML, Programming, Study Logs, and Skill Streaks.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import LearningGoal, LearningSession
from ai_engine.learning_ai import generate_learning_roadmap


@login_required
def learning_dashboard_view(request):
    """Main Learning & Knowledge development page."""
    goals = LearningGoal.objects.filter(user=request.user)
    recent_sessions = LearningSession.objects.filter(goal__user=request.user)[:10]

    total_study_minutes = sum(s.duration_minutes for s in recent_sessions)
    total_problems = sum(s.practice_problems_solved for s in recent_sessions)

    context = {
        'goals': goals,
        'recent_sessions': recent_sessions,
        'total_study_hours': round(total_study_minutes / 60.0, 1),
        'total_problems': total_problems,
        'show_nav': True,
        'active_nav': 'learning',
    }
    return render(request, 'learning/index.html', context)


@login_required
def create_roadmap_api(request):
    """Generate and create a structured multi-week roadmap for a skill."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    topic = request.POST.get('topic', '').strip()
    category = request.POST.get('category', 'programming')
    target_hours = int(request.POST.get('target_hours', 40))

    if not topic:
        return JsonResponse({'error': 'Topic required'}, status=400)

    # Generate AI roadmap
    ai_roadmap_data = generate_learning_roadmap(topic, category, target_hours)

    goal = LearningGoal.objects.create(
        user=request.user,
        title=topic,
        category=category,
        target_hours=target_hours,
        roadmap=ai_roadmap_data.get('weeks', []),
        current_topic=ai_roadmap_data.get('weeks', [{}])[0].get('week_title', topic)
    )

    return JsonResponse({
        'status': 'ok',
        'goal_id': goal.id,
        'title': goal.title,
        'roadmap': goal.roadmap,
    })


@login_required
def toggle_roadmap_topic_api(request):
    """Mark a week or subtopic in a learning roadmap as completed."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    goal_id = request.POST.get('goal_id')
    week_number = int(request.POST.get('week_number', 1))

    try:
        goal = LearningGoal.objects.get(id=goal_id, user=request.user)
        for w in goal.roadmap:
            if w.get('week_number') == week_number:
                w['completed'] = not w.get('completed', False)
                break
        goal.save()
        return JsonResponse({'status': 'ok', 'progress': goal.progress_percentage})
    except LearningGoal.DoesNotExist:
        return JsonResponse({'error': 'Goal not found'}, status=404)


@login_required
def log_study_session_api(request):
    """Log study time and practice problems for a learning goal."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    goal_id = request.POST.get('goal_id')
    duration_minutes = int(request.POST.get('duration_minutes', 45))
    topics_covered = request.POST.get('topics_covered', '')
    problems_solved = int(request.POST.get('problems_solved', 0))

    try:
        goal = LearningGoal.objects.get(id=goal_id, user=request.user)
        session = LearningSession.objects.create(
            goal=goal,
            duration_minutes=duration_minutes,
            topics_covered=topics_covered,
            practice_problems_solved=problems_solved
        )
        goal.completed_hours += duration_minutes / 60.0
        goal.save()
        return JsonResponse({'status': 'ok', 'completed_hours': round(goal.completed_hours, 1)})
    except LearningGoal.DoesNotExist:
        return JsonResponse({'error': 'Goal not found'}, status=404)
