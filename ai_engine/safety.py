"""
Safety guardrails and validation rules for health, nutrition, and workout advice.
"""
import re


MIN_DAILY_CALORIES_MALE = 1500
MIN_DAILY_CALORIES_FEMALE = 1200
MAX_SAFE_DEFICIT_CALORIES = 1000

MEDICAL_DISCLAIMER = (
    "Note: SelfDev AI provides fitness, habit, and nutrition coaching for educational and "
    "self-improvement purposes. It is not a substitute for professional medical advice, diagnosis, "
    "or physical therapy. Always consult a healthcare professional before starting any new training or diet regimen."
)


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """Sanitize user input before passing to AI models."""
    if not text:
        return ""
    # Strip dangerous control characters and trim
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    return cleaned.strip()[:max_length]


def validate_nutrition_estimates(totals: dict) -> dict:
    """Clamp and sanitize AI nutrition estimates to realistic physiological bounds."""
    calories = max(0.0, min(float(totals.get('calories', 0)), 5000.0))
    protein = max(0.0, min(float(totals.get('protein', 0)), 300.0))
    carbs = max(0.0, min(float(totals.get('carbs', 0)), 600.0))
    fat = max(0.0, min(float(totals.get('fat', 0)), 300.0))
    fiber = max(0.0, min(float(totals.get('fiber', 0)), 100.0))

    return {
        'calories': round(calories, 1),
        'protein': round(protein, 1),
        'carbs': round(carbs, 1),
        'fat': round(fat, 1),
        'fiber': round(fiber, 1),
    }


def check_for_medical_red_flags(user_message: str) -> bool:
    """Check if the user message contains symptoms requiring immediate medical advice."""
    red_flags = [
        'chest pain', 'heart attack', 'cannot breathe', 'severe dizziness',
        'passed out', 'broken bone', 'sharp tearing pain', 'dislocated',
        'blood in urine', 'blood in stool', 'concussion', 'fainted'
    ]
    lowered = user_message.lower()
    return any(flag in lowered for flag in red_flags)


def format_medical_warning() -> str:
    """Immediate warning for acute medical red flags."""
    return (
        "⚠️ **URGENT HEALTH NOTICE**: You mentioned symptoms that could indicate an acute medical injury or condition. "
        "Please stop all physical activity immediately and seek medical attention from a doctor or emergency healthcare provider."
    )
