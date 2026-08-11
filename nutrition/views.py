"""
Nutrition views — Food logging, photo analysis, daily nutrition summary.
"""
import json
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from .models import FoodLog, MealEntry
from dashboard.models import DailyProgress


@login_required
def food_log_view(request):
    """Food logging page with daily summary."""
    today = timezone.now().date()
    date_str = request.GET.get('date')
    if date_str:
        try:
            from datetime import datetime
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    meals = FoodLog.objects.filter(user=request.user, date=selected_date).prefetch_related('entries')

    # Daily totals
    daily_totals = {
        'calories': sum(m.total_calories for m in meals),
        'protein': sum(m.total_protein for m in meals),
        'carbs': sum(m.total_carbs for m in meals),
        'fat': sum(m.total_fat for m in meals),
        'fiber': sum(m.total_fiber for m in meals),
    }

    profile = request.user.profile

    context = {
        'meals': meals,
        'daily_totals': daily_totals,
        'selected_date': selected_date,
        'is_today': selected_date == today,
        'calorie_target': profile.calorie_target or profile.estimated_daily_calories or 2000,
        'protein_target': profile.protein_target_grams or profile.estimated_protein_grams or 100,
        'show_nav': True,
        'active_nav': 'food',
    }
    return render(request, 'nutrition/log.html', context)


@login_required
def add_meal_view(request):
    """Add a new meal manually or via photo analysis."""
    if request.method == 'POST':
        meal_type = request.POST.get('meal_type', 'lunch')
        photo = request.FILES.get('photo')
        today = timezone.now().date()

        food_log = FoodLog.objects.create(
            user=request.user,
            date=today,
            meal_type=meal_type,
            photo=photo,
        )

        # If photo provided, attempt AI analysis
        if photo and settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here':
            try:
                from ai_engine.nutrition_ai import analyze_food_photo
                photo.seek(0)
                photo_data = base64.b64encode(photo.read()).decode('utf-8')
                result = analyze_food_photo(photo_data)
                if result and 'items' in result:
                    for item in result['items']:
                        MealEntry.objects.create(
                            food_log=food_log,
                            food_name=item.get('name', 'Unknown'),
                            portion_size=item.get('portion', ''),
                            calories=item.get('calories', 0),
                            protein=item.get('protein', 0),
                            carbs=item.get('carbs', 0),
                            fat=item.get('fat', 0),
                            fiber=item.get('fiber', 0),
                        )
                    food_log.ai_analyzed = True
                    food_log.ai_raw_response = json.dumps(result)
                    food_log.update_totals()
            except Exception as e:
                food_log.notes = f"AI analysis failed: {str(e)}"
                food_log.save()

        # Handle manual entries
        food_names = request.POST.getlist('food_name')
        calories_list = request.POST.getlist('calories')
        protein_list = request.POST.getlist('protein')
        carbs_list = request.POST.getlist('carbs')
        fat_list = request.POST.getlist('fat')
        portions = request.POST.getlist('portion_size')

        for i, name in enumerate(food_names):
            if name.strip():
                MealEntry.objects.create(
                    food_log=food_log,
                    food_name=name.strip(),
                    portion_size=portions[i] if i < len(portions) else '',
                    calories=float(calories_list[i]) if i < len(calories_list) and calories_list[i] else 0,
                    protein=float(protein_list[i]) if i < len(protein_list) and protein_list[i] else 0,
                    carbs=float(carbs_list[i]) if i < len(carbs_list) and carbs_list[i] else 0,
                    fat=float(fat_list[i]) if i < len(fat_list) and fat_list[i] else 0,
                )

        food_log.update_totals()

        # Update daily progress
        _sync_daily_nutrition(request.user, today)

        return redirect('nutrition:log')

    context = {
        'meal_types': FoodLog.MEAL_TYPE_CHOICES,
        'show_nav': True,
        'active_nav': 'food',
        'has_ai': settings.GROQ_API_KEY and settings.GROQ_API_KEY != 'your-groq-api-key-here',
    }
    return render(request, 'nutrition/add_meal.html', context)


@login_required
def analyze_photo_api(request):
    """AJAX: Analyze uploaded food photo with AI."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    photo = request.FILES.get('photo')
    if not photo:
        return JsonResponse({'error': 'No photo provided'}, status=400)

    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == 'your-groq-api-key-here':
        return JsonResponse({'error': 'AI not configured. Add your GROQ_API_KEY to .env'}, status=400)

    try:
        from ai_engine.nutrition_ai import analyze_food_photo
        photo_data = base64.b64encode(photo.read()).decode('utf-8')
        result = analyze_food_photo(photo_data)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def update_meal_entry(request):
    """AJAX: Update or delete a meal entry."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    action = request.POST.get('action')
    entry_id = request.POST.get('entry_id')

    try:
        entry = MealEntry.objects.get(id=entry_id, food_log__user=request.user)

        if action == 'delete':
            food_log = entry.food_log
            entry.delete()
            food_log.update_totals()
            _sync_daily_nutrition(request.user, food_log.date)
            return JsonResponse({'status': 'ok'})

        elif action == 'update':
            entry.food_name = request.POST.get('food_name', entry.food_name)
            entry.portion_size = request.POST.get('portion_size', entry.portion_size)
            entry.calories = float(request.POST.get('calories', entry.calories))
            entry.protein = float(request.POST.get('protein', entry.protein))
            entry.carbs = float(request.POST.get('carbs', entry.carbs))
            entry.fat = float(request.POST.get('fat', entry.fat))
            entry.fiber = float(request.POST.get('fiber', entry.fiber))
            entry.user_corrected = True
            entry.save()

            entry.food_log.update_totals()
            _sync_daily_nutrition(request.user, entry.food_log.date)
            return JsonResponse({'status': 'ok'})

    except MealEntry.DoesNotExist:
        return JsonResponse({'error': 'Entry not found'}, status=404)

    return JsonResponse({'error': 'Invalid action'}, status=400)


def _sync_daily_nutrition(user, date):
    """Sync daily nutrition totals from food logs to DailyProgress."""
    meals = FoodLog.objects.filter(user=user, date=date)
    daily, _ = DailyProgress.objects.get_or_create(user=user, date=date)
    daily.calories_consumed = sum(m.total_calories for m in meals)
    daily.protein_consumed = sum(m.total_protein for m in meals)
    daily.carbs_consumed = sum(m.total_carbs for m in meals)
    daily.fat_consumed = sum(m.total_fat for m in meals)
    daily.calculate_score()
    daily.save()
