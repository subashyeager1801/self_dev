"""
Account forms — Registration, Login, Profile setup wizard.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile


class RegisterForm(UserCreationForm):
    """User registration form."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email address',
            'id': 'id_email',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Choose a username',
            'password1': 'Create a password',
            'password2': 'Confirm password',
        }
        for field_name, placeholder in placeholders.items():
            self.fields[field_name].widget.attrs.update({
                'class': 'form-input',
                'placeholder': placeholder,
            })
            self.fields[field_name].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(user=user)
        return user


class LoginForm(AuthenticationForm):
    """Custom login form with styled inputs."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password',
        })


class ProfileStep1Form(forms.ModelForm):
    """Step 1: Personal information."""
    first_name = forms.CharField(
        max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your name'})
    )

    class Meta:
        model = UserProfile
        fields = ['age', 'gender', 'height_cm', 'weight_kg', 'target_weight_kg']
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Your age', 'min': 13, 'max': 100
            }),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'height_cm': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Height in cm', 'step': '0.1'
            }),
            'weight_kg': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Current weight in kg', 'step': '0.1'
            }),
            'target_weight_kg': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Target weight in kg', 'step': '0.1'
            }),
        }


class ProfileStep2Form(forms.ModelForm):
    """Step 2: Fitness goals and experience."""
    class Meta:
        model = UserProfile
        fields = ['fitness_goal', 'body_goal', 'fitness_experience']
        widgets = {
            'fitness_goal': forms.RadioSelect(),
            'body_goal': forms.Textarea(attrs={
                'class': 'form-textarea', 'placeholder': 'Describe your ideal body goal...',
                'rows': 3,
            }),
            'fitness_experience': forms.RadioSelect(),
        }


class ProfileStep3Form(forms.ModelForm):
    """Step 3: Workout preferences."""
    class Meta:
        model = UserProfile
        fields = ['workout_location', 'daily_workout_minutes', 'workout_days_per_week']
        widgets = {
            'workout_location': forms.RadioSelect(),
            'daily_workout_minutes': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Minutes per day', 'min': 10, 'max': 180
            }),
            'workout_days_per_week': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Days per week', 'min': 1, 'max': 7
            }),
        }


EQUIPMENT_CHOICES = [
    ('no_equipment', 'No Equipment (Bodyweight Only)'),
    ('dumbbells', 'Dumbbells'),
    ('resistance_bands', 'Resistance Bands'),
    ('pull_up_bar', 'Pull-up Bar'),
    ('bench', 'Bench'),
    ('barbell', 'Barbell + Plates'),
    ('kettlebell', 'Kettlebell'),
    ('jump_rope', 'Jump Rope'),
    ('yoga_mat', 'Yoga Mat'),
]

GYM_EQUIPMENT_CHOICES = [
    ('full_gym', 'Standard Gym (All Equipment)'),
    ('dumbbells', 'Dumbbells'),
    ('barbell', 'Barbell + Plates'),
    ('cables', 'Cable Machine'),
    ('smith_machine', 'Smith Machine'),
    ('leg_press', 'Leg Press'),
    ('pull_up_bar', 'Pull-up Bar'),
    ('bench', 'Flat & Incline Bench'),
    ('treadmill', 'Treadmill'),
    ('rowing_machine', 'Rowing Machine'),
]


class ProfileStep4Form(forms.ModelForm):
    """Step 4: Daily targets."""
    class Meta:
        model = UserProfile
        fields = ['sleep_target_hours', 'water_target_liters', 'self_dev_goals']
        widgets = {
            'sleep_target_hours': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Hours of sleep', 'step': '0.5',
                'min': 4, 'max': 12,
            }),
            'water_target_liters': forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Liters of water', 'step': '0.5',
                'min': 1, 'max': 10,
            }),
            'self_dev_goals': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'e.g. Learn Python, Read 20 books, Master DSA, Improve discipline...',
                'rows': 3,
            }),
        }
