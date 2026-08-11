"""
AI Nutrition analysis for photos and meal generation.
"""
import json
import logging
from .client import vision_completion, chat_completion
from .prompts import FOOD_PHOTO_ANALYSIS_PROMPT
from .safety import validate_nutrition_estimates

logger = logging.getLogger(__name__)


def analyze_food_photo(image_base64: str) -> dict:
    """
    Analyze a food photo using Groq Vision API.
    Returns structured nutritional estimates and detected food items.
    """
    try:
        raw_response = vision_completion(
            image_base64=image_base64,
            prompt=FOOD_PHOTO_ANALYSIS_PROMPT,
            max_tokens=1200
        )

        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        data = json.loads(clean_json)

        # Validate and sanitize totals
        if 'totals' in data:
            data['totals'] = validate_nutrition_estimates(data['totals'])

        return data
    except Exception as e:
        logger.warning(f"Groq Vision photo analysis failed or unavailable: {e}")
        # Return a structured fallback response
        return {
            "meal_name": "Uploaded Meal",
            "confidence": "low",
            "disclaimer": "AI Vision model did not return structured data. Please enter items manually.",
            "items": [
                {
                    "name": "General Balanced Meal Item",
                    "portion": "1 serving",
                    "calories": 400,
                    "protein": 25.0,
                    "carbs": 45.0,
                    "fat": 12.0,
                    "fiber": 4.0
                }
            ],
            "totals": {
                "calories": 400.0,
                "protein": 25.0,
                "carbs": 45.0,
                "fat": 12.0,
                "fiber": 4.0
            },
            "nutritionist_insight": "Adjust the items and portion sizes above to match your actual plate."
        }


def generate_meal_suggestion(user_profile: dict, remaining_macros: dict) -> str:
    """Generate high-protein or goal-aligned meal recommendations to hit remaining daily targets."""
    prompt = f"""As a nutrition coach, suggest 2 quick, delicious meal or snack options to help the user hit their targets.
User Goal: {user_profile.get('fitness_goal', 'fitness')}
Remaining Target Today:
- Calories: {remaining_macros.get('calories', 500)} kcal
- Protein: {remaining_macros.get('protein', 30)} g
- Carbs: {remaining_macros.get('carbs', 40)} g
- Fat: {remaining_macros.get('fat', 15)} g

Provide the recipe names, quick ingredient list, and macro breakdown for each."""

    messages = [
        {"role": "system", "content": "You are an expert sports nutritionist."},
        {"role": "user", "content": prompt}
    ]

    try:
        return chat_completion(messages, temperature=0.7, max_tokens=800)
    except Exception as e:
        logger.error(f"Meal suggestion generation failed: {e}")
        return "Option 1: Grilled Chicken Breast (150g) with Steamed Jasmine Rice (1 cup) & Broccoli.\nOption 2: Greek Yogurt (200g) with 1 scoop whey protein, handful of berries, and 1 tbsp chia seeds."
