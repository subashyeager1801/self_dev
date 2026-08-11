"""
Account views — Registration, Login, Logout, Profile setup wizard.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import (
    RegisterForm, LoginForm,
    ProfileStep1Form, ProfileStep2Form, ProfileStep3Form, ProfileStep4Form,
    EQUIPMENT_CHOICES, GYM_EQUIPMENT_CHOICES,
)
from .models import UserProfile


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Welcome! Let\'s set up your profile.')
            return redirect('accounts:profile_setup')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Check if profile is complete
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.profile_completed:
                return redirect('accounts:profile_setup')
            return redirect('dashboard:home')
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'You\'ve been logged out.')
    return redirect('accounts:login')


@login_required
def profile_setup_view(request):
    """Multi-step profile setup wizard."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    step = int(request.GET.get('step', profile.onboarding_step))

    # Clamp step to valid range
    step = max(1, min(step, 5))

    if request.method == 'POST':
        if step == 1:
            form = ProfileStep1Form(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                request.user.first_name = form.cleaned_data['first_name']
                request.user.save()
                profile.onboarding_step = 2
                profile.save()
                return redirect('accounts:profile_setup')

        elif step == 2:
            form = ProfileStep2Form(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.onboarding_step = 3
                profile.save()
                return redirect('accounts:profile_setup')

        elif step == 3:
            form = ProfileStep3Form(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.onboarding_step = 4
                profile.save()
                return redirect('accounts:profile_setup')

        elif step == 4:
            # Equipment selection (handled via POST data)
            selected_equipment = request.POST.getlist('equipment')
            profile.available_equipment = selected_equipment
            profile.onboarding_step = 5
            profile.save()
            return redirect('accounts:profile_setup')

        elif step == 5:
            form = ProfileStep4Form(request.POST, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                # Auto-calculate nutrition targets
                if not profile.calorie_target:
                    profile.calorie_target = profile.estimated_daily_calories
                if not profile.protein_target_grams:
                    profile.protein_target_grams = profile.estimated_protein_grams
                profile.profile_completed = True
                profile.onboarding_step = 5
                profile.save()
                messages.success(request, 'Profile setup complete! Welcome to your dashboard.')
                return redirect('dashboard:home')
    else:
        if step == 1:
            initial = {'first_name': request.user.first_name}
            form = ProfileStep1Form(instance=profile, initial=initial)
        elif step == 2:
            form = ProfileStep2Form(instance=profile)
        elif step == 3:
            form = ProfileStep3Form(instance=profile)
        elif step == 4:
            form = None  # Equipment uses custom template
        elif step == 5:
            form = ProfileStep4Form(instance=profile)
        else:
            form = None

    # Prepare equipment choices for step 4
    equipment_choices = (
        GYM_EQUIPMENT_CHOICES if profile.workout_location == 'gym'
        else EQUIPMENT_CHOICES
    )

    context = {
        'form': form,
        'step': step,
        'total_steps': 5,
        'profile': profile,
        'equipment_choices': equipment_choices,
        'selected_equipment': profile.available_equipment or [],
        'step_titles': {
            1: 'Personal Information',
            2: 'Fitness Goals',
            3: 'Workout Preferences',
            4: 'Equipment',
            5: 'Daily Targets',
        },
        'step_icons': {
            1: '👤',
            2: '🎯',
            3: '💪',
            4: '🏋️',
            5: '📊',
        },
    }
    return render(request, 'accounts/profile_setup.html', context)


@login_required
def profile_view(request):
    """View and edit user profile."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Handle profile updates via AJAX
        field = request.POST.get('field')
        value = request.POST.get('value')

        if field and hasattr(profile, field):
            # Type coercion
            field_obj = UserProfile._meta.get_field(field)
            if isinstance(field_obj, (models.FloatField,)):
                value = float(value) if value else None
            elif isinstance(field_obj, (models.PositiveIntegerField, models.IntegerField)):
                value = int(value) if value else None

            setattr(profile, field, value)
            profile.save()
            return JsonResponse({'status': 'ok'})

        return JsonResponse({'status': 'error'}, status=400)

    context = {
        'profile': profile,
        'bmi': profile.bmi,
        'estimated_calories': profile.estimated_daily_calories,
        'estimated_protein': profile.estimated_protein_grams,
    }
    return render(request, 'accounts/profile.html', context)
