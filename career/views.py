"""
Career views — Target Role, Skill Gap Matrix, Milestones, and Interview Readiness.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import CareerProfile, CareerSkill, CareerMilestone
from ai_engine.career_ai import analyze_career_path


@login_required
def career_dashboard_view(request):
    """Main Career Development and Skill Gap Matrix page."""
    profile, _ = CareerProfile.objects.get_or_create(user=request.user)
    skills = CareerSkill.objects.filter(user=request.user)
    milestones = CareerMilestone.objects.filter(user=request.user)

    completed_milestones = milestones.filter(completed=True).count()

    context = {
        'profile': profile,
        'skills': skills,
        'milestones': milestones,
        'completed_milestones': completed_milestones,
        'total_milestones': milestones.count(),
        'show_nav': True,
        'active_nav': 'career',
    }
    return render(request, 'career/index.html', context)


@login_required
def update_career_profile_api(request):
    """Update user's target role and trigger AI skill gap analysis."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    target_role = request.POST.get('target_role', '').strip()
    if not target_role:
        return JsonResponse({'error': 'Target role required'}, status=400)

    profile, _ = CareerProfile.objects.get_or_create(user=request.user)
    profile.target_role = target_role
    profile.save()

    # Get current and gap skills
    current_skills = list(CareerSkill.objects.filter(user=request.user, proficiency__in=['competent', 'advanced']).values_list('skill_name', flat=True))
    gap_skills = list(CareerSkill.objects.filter(user=request.user, proficiency='learning').values_list('skill_name', flat=True))

    ai_analysis = analyze_career_path(target_role, current_skills, gap_skills)
    profile.interview_readiness_score = ai_analysis.get('readiness_score', 60)
    profile.save()

    return JsonResponse({
        'status': 'ok',
        'target_role': profile.target_role,
        'readiness': profile.interview_readiness_score,
        'ai_analysis': ai_analysis
    })


@login_required
def manage_skill_api(request):
    """Add, update, or delete a skill in the matrix."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    action = request.POST.get('action')
    if action == 'add':
        name = request.POST.get('name', '').strip()
        proficiency = request.POST.get('proficiency', 'learning')
        if name:
            CareerSkill.objects.update_or_create(
                user=request.user,
                skill_name=name,
                defaults={'proficiency': proficiency}
            )
            return JsonResponse({'status': 'ok'})

    elif action == 'toggle_proficiency':
        skill_id = request.POST.get('skill_id')
        try:
            skill = CareerSkill.objects.get(id=skill_id, user=request.user)
            cycle = {'learning': 'competent', 'competent': 'advanced', 'advanced': 'learning'}
            skill.proficiency = cycle.get(skill.proficiency, 'competent')
            skill.save()
            return JsonResponse({'status': 'ok', 'new_proficiency': skill.proficiency, 'label': skill.get_proficiency_display()})
        except CareerSkill.DoesNotExist:
            return JsonResponse({'error': 'Skill not found'}, status=404)

    return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
def manage_milestone_api(request):
    """Add or toggle completion of career milestones."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    action = request.POST.get('action')
    if action == 'add':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'project')
        if title:
            CareerMilestone.objects.create(user=request.user, title=title, category=category)
            return JsonResponse({'status': 'ok'})

    elif action == 'toggle':
        m_id = request.POST.get('milestone_id')
        try:
            milestone = CareerMilestone.objects.get(id=m_id, user=request.user)
            milestone.completed = not milestone.completed
            milestone.save()
            return JsonResponse({'status': 'ok', 'completed': milestone.completed})
        except CareerMilestone.DoesNotExist:
            return JsonResponse({'error': 'Milestone not found'}, status=404)

    return JsonResponse({'error': 'Invalid action'}, status=400)
