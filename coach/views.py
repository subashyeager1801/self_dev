"""
Coach views — AI Chat, daily coaching, and motivation.
"""
import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from .models import AIConversation, AIMessage, AIRecommendation, AIMemoryItem
from dashboard.models import DailyProgress
from workouts.models import WorkoutSession
from growth.models import Goal


@login_required
def memory_view(request):
    """View and manage what AI remembers about the user."""
    memories = AIMemoryItem.objects.filter(user=request.user)
    context = {
        'memories': memories,
        'show_nav': True,
        'active_nav': 'coach',
    }
    return render(request, 'coach/memory.html', context)


@login_required
def manage_memory_api(request):
    """AJAX: Edit, delete, or add AI memories."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    action = request.POST.get('action')
    if action == 'delete':
        mem_id = request.POST.get('memory_id')
        AIMemoryItem.objects.filter(id=mem_id, user=request.user).delete()
        return JsonResponse({'status': 'ok'})

    elif action == 'create':
        title = request.POST.get('title', '').strip()
        detail = request.POST.get('detail', '').strip()
        category = request.POST.get('category', 'preference')
        if title:
            AIMemoryItem.objects.create(user=request.user, title=title, detail=detail, category=category)
            return JsonResponse({'status': 'ok'})

    return JsonResponse({'error': 'Invalid action'}, status=400)


@login_required
def chat_view(request):
    """AI Coach chat page."""
    # Get or create conversation
    conversation = AIConversation.objects.filter(user=request.user).first()
    if not conversation:
        conversation = AIConversation.objects.create(user=request.user, title='Coach Chat')

    messages = conversation.messages.all()[:50]

    context = {
        'conversation': conversation,
        'messages': messages,
        'has_ai': bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here'),
        'show_nav': True,
        'active_nav': 'coach',
    }
    return render(request, 'coach/chat.html', context)


@login_required
def send_message_api(request):
    """AJAX: Send a message to the AI coach."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    user_message = request.POST.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message required'}, status=400)

    # Get or create conversation
    conversation = AIConversation.objects.filter(user=request.user).first()
    if not conversation:
        conversation = AIConversation.objects.create(user=request.user)

    # Save user message
    AIMessage.objects.create(conversation=conversation, role='user', content=user_message)

    # Generate AI response
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here':
        try:
            from ai_engine.chat_ai import get_chat_response
            from ai_engine.memory_ai import extract_memories

            user_context = _build_user_context(request.user)

            # Auto-extract new memories in background
            existing_mems = list(AIMemoryItem.objects.filter(user=request.user).values('category', 'title', 'detail'))
            new_mems = extract_memories(user_message, existing_mems)
            for m in new_mems:
                AIMemoryItem.objects.create(
                    user=request.user,
                    category=m.get('category', 'preference'),
                    title=m.get('title', 'Observation'),
                    detail=m.get('detail', ''),
                    confidence=m.get('confidence', 'High')
                )

            # Get recent conversation history
            recent_messages = conversation.messages.order_by('-created_at')[:20]
            history = [{'role': m.role, 'content': m.content} for m in reversed(recent_messages)]

            ai_response = get_chat_response(user_message, user_context, history)
        except Exception as e:
            ai_response = f"I'm having trouble connecting right now. Please try again. (Error: {str(e)})"
    else:
        ai_response = _get_fallback_response(user_message, request.user)

    # Save AI response
    AIMessage.objects.create(conversation=conversation, role='assistant', content=ai_response)
    conversation.save()  # Update timestamp

    return JsonResponse({
        'status': 'ok',
        'response': ai_response,
    })


@login_required
def daily_coaching_view(request):
    """Daily AI coaching page with plan and motivation."""
    profile = request.user.profile
    today = timezone.now().date()

    daily, _ = DailyProgress.objects.get_or_create(user=request.user, date=today)
    daily.calculate_score()
    daily.save()

    # Get or generate today's recommendation
    recommendation = AIRecommendation.objects.filter(
        user=request.user, date=today, rec_type='daily_plan'
    ).first()

    motivation = AIRecommendation.objects.filter(
        user=request.user, date=today, rec_type='motivation'
    ).first()

    if not recommendation:
        plan_content = _generate_daily_plan(request.user, profile, daily)
        recommendation = AIRecommendation.objects.create(
            user=request.user, rec_type='daily_plan',
            content=plan_content, date=today
        )

    if not motivation:
        motivation_content = _generate_motivation(request.user, profile, daily)
        motivation = AIRecommendation.objects.create(
            user=request.user, rec_type='motivation',
            content=motivation_content, date=today
        )

    context = {
        'profile': profile,
        'daily': daily,
        'recommendation': recommendation,
        'motivation': motivation,
        'show_nav': True,
        'active_nav': 'coach',
    }
    return render(request, 'coach/daily.html', context)


def _build_user_context(user):
    """Build structured context about the user for AI."""
    profile = user.profile
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    # Recent daily progress
    recent_daily = DailyProgress.objects.filter(
        user=user, date__gte=week_ago
    ).order_by('date')

    # Recent workouts
    recent_workouts = WorkoutSession.objects.filter(
        user=user, date__gte=week_ago
    ).order_by('-date')[:5]

    # Active goals
    goals = Goal.objects.filter(user=user, is_active=True)[:10]

    context = {
        'name': profile.get_display_name(),
        'age': profile.age,
        'weight': profile.weight_kg,
        'target_weight': profile.target_weight_kg,
        'fitness_goal': profile.get_fitness_goal_display(),
        'experience': profile.get_fitness_experience_display(),
        'workout_location': profile.get_workout_location_display(),
        'daily_workout_minutes': profile.daily_workout_minutes,
        'workout_days_per_week': profile.workout_days_per_week,
        'sleep_target': profile.sleep_target_hours,
        'water_target': profile.water_target_liters,
        'calorie_target': profile.calorie_target or profile.estimated_daily_calories,
        'protein_target': profile.protein_target_grams or profile.estimated_protein_grams,
        'recent_scores': [
            {'date': str(d.date), 'score': d.daily_score, 'workout': d.workout_completed,
             'protein': d.protein_consumed, 'water': d.water_liters, 'sleep': d.sleep_hours}
            for d in recent_daily
        ],
        'recent_workouts': [
            {'title': w.title, 'date': str(w.date), 'status': w.status,
             'completion': w.completion_percentage}
            for w in recent_workouts
        ],
        'goals': [
            {'title': g.title, 'progress': g.progress_percentage, 'type': g.goal_type}
            for g in goals
        ],
    }
    return context


def _generate_daily_plan(user, profile, daily):
    """Generate a daily plan — uses AI if available, otherwise rule-based."""
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here':
        try:
            from ai_engine.coach_ai import generate_daily_plan
            context = _build_user_context(user)
            return generate_daily_plan(context)
        except Exception:
            pass

    # Fallback rule-based plan
    goals = Goal.objects.filter(user=user, is_active=True)[:3]
    plan = f"Today's Priorities:\n\n"
    plan += f"1. {'Complete your workout' if not daily.workout_completed else '✓ Workout done!'}\n"
    plan += f"2. Reach your protein target ({profile.protein_target_grams or profile.estimated_protein_grams or 100}g)\n"

    for i, goal in enumerate(goals, 3):
        plan += f"{i}. Work on: {goal.title} ({goal.progress_percentage}% done)\n"

    plan += f"\n{len(goals) + 3}. Drink {profile.water_target_liters}L water\n"
    plan += f"{len(goals) + 4}. Sleep by your target time ({profile.sleep_target_hours}h)\n"

    return plan


def _generate_motivation(user, profile, daily):
    """Generate contextual motivation — uses AI if available, otherwise rule-based."""
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here':
        try:
            from ai_engine.coach_ai import generate_motivation
            context = _build_user_context(user)
            return generate_motivation(context)
        except Exception:
            pass

    # Fallback rule-based motivation
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)

    workouts_this_week = WorkoutSession.objects.filter(
        user=user, date__gte=week_ago, status='completed'
    ).count()

    recent_scores = DailyProgress.objects.filter(
        user=user, date__gte=week_ago
    ).values_list('daily_score', flat=True)

    avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0

    if workouts_this_week >= profile.workout_days_per_week:
        return f"You've completed {workouts_this_week} workouts this week. Your consistency is becoming a habit. Keep the momentum going."
    elif workouts_this_week == 0:
        return "You haven't worked out this week yet. Don't try to make up for lost days with an extreme session. Start with today's planned workout."
    elif avg_score >= 70:
        return f"Your average daily score is {int(avg_score)}. You're building a strong routine. Focus on the areas that need a push."
    else:
        return "Progress isn't always linear. Focus on one small win today — just one. That's enough to restart momentum."


def _get_fallback_response(message, user):
    """Fallback rule-based chat response when AI is not available."""
    message_lower = message.lower()
    profile = user.profile

    if any(w in message_lower for w in ['workout', 'exercise', 'train']):
        return (f"Based on your {profile.get_fitness_goal_display()} goal and "
                f"{profile.get_fitness_experience_display()} experience level, I recommend "
                f"going to the Workout page to generate today's workout. Focus on proper form "
                f"and don't skip your rest periods.")
    elif any(w in message_lower for w in ['eat', 'food', 'meal', 'diet', 'nutrition']):
        cal = profile.calorie_target or profile.estimated_daily_calories or 2000
        prot = profile.protein_target_grams or profile.estimated_protein_grams or 100
        return (f"For your {profile.get_fitness_goal_display()} goal, aim for ~{cal} kcal and "
                f"~{prot}g protein daily. Focus on whole foods, lean proteins, and vegetables. "
                f"Log your meals in the Food section to track progress.")
    elif any(w in message_lower for w in ['sleep', 'tired', 'rest']):
        return (f"Your sleep target is {profile.sleep_target_hours} hours. Quality sleep is "
                f"essential for recovery and progress. Try to maintain a consistent bedtime, "
                f"avoid screens 30 minutes before bed, and keep your room cool.")
    elif any(w in message_lower for w in ['progress', 'slow', 'results', 'improve']):
        return ("Progress takes time. Focus on consistency rather than perfection. Track your "
                "daily habits, hit your protein target, sleep well, and the results will follow. "
                "Check your Progress page for trends.")
    elif any(w in message_lower for w in ['miss', 'skip', 'forgot']):
        return ("Don't stress about missing a day. The key is getting back on track. "
                "Don't try to compensate with extra workouts — just follow today's planned session. "
                "Consistency over intensity.")
    elif any(w in message_lower for w in ['today', 'plan', 'do']):
        return ("Go to the Home page to see today's priorities. Focus on: workout, protein target, "
                "water intake, and one learning goal. Small daily actions compound into big results.")
    else:
        return (f"I'm your AI coach, {profile.get_display_name()}! I can help with workout advice, "
                f"nutrition guidance, sleep tips, and motivation. Try asking me specific questions like "
                f"'What should I eat today?' or 'How's my progress this week?'\n\n"
                f"💡 For full AI coaching, add your GROQ_API_KEY to the .env file.")
