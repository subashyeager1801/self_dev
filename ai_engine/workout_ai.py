"""
AI Workout Generation and Adaptation logic.
"""
import json
import logging
from .client import chat_completion
from .prompts import WORKOUT_GENERATION_PROMPT

logger = logging.getLogger(__name__)


def generate_custom_workout(profile_data: dict, target_muscles: list, recent_history: list = None) -> dict:
    """
    Generate an AI workout plan tailored to the user profile and equipment.
    Returns a structured dictionary with overview, warmup, exercises, and cooldown.
    """
    prompt = WORKOUT_GENERATION_PROMPT.format(
        fitness_goal=profile_data.get('fitness_goal', 'general fitness'),
        experience=profile_data.get('fitness_experience', 'intermediate'),
        location=profile_data.get('workout_location', 'gym'),
        equipment=', '.join(profile_data.get('available_equipment', [])) or 'Standard Gym Equipment',
        available_minutes=profile_data.get('daily_workout_minutes', 45),
        target_muscles=', '.join(target_muscles) if target_muscles else 'Full Body',
        recent_history=json.dumps(recent_history or [])
    )

    messages = [
        {"role": "system", "content": "You are a professional strength coach. Always respond in strict JSON."},
        {"role": "user", "content": prompt}
    ]

    try:
        raw_response = chat_completion(messages, temperature=0.5, max_tokens=1500)
        # Clean JSON markdown fences if present
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        data = json.loads(clean_json)
        return data
    except Exception as e:
        logger.warning(f"AI workout generation failed: {e}. Falling back to rule-based generation.")
        return generate_fallback_workout(profile_data, target_muscles)


def generate_fallback_workout(profile_data: dict, target_muscles: list) -> dict:
    """Deterministic rule-based fallback workout generator when AI API is unavailable."""
    goal = profile_data.get('fitness_goal', 'general')
    location = profile_data.get('workout_location', 'gym')
    duration = profile_data.get('daily_workout_minutes', 45)

    muscle_str = " + ".join([m.capitalize() for m in target_muscles]) if target_muscles else "Full Body"
    title = f"{muscle_str} Power Session"

    # Default sets/reps based on goal
    goal_reps = {
        'fat_loss': ('3', '12-15', 45),
        'muscle_gain': ('4', '8-12', 75),
        'athletic': ('3', '10-12', 60),
        'strength': ('5', '3-5', 120),
        'maintain': ('3', '10', 60),
    }.get(goal, ('3', '10-12', 60))

    sets, reps, rest = goal_reps

    return {
        "title": title,
        "overview": f"A targeted session designed for {goal.replace('_', ' ')} focusing on {muscle_str.lower()}.",
        "warmup": [
            {"exercise": "Arm Circles & Torso Twists", "duration_or_reps": "3 minutes", "notes": "Increase core temperature"},
            {"exercise": "Bodyweight Squats & Jumping Jacks", "duration_or_reps": "2 minutes", "notes": "Elevate heart rate"}
        ],
        "exercises": [
            {
                "name": f"Compound Movement for {target_muscles[0].capitalize() if target_muscles else 'Body'}",
                "muscle_group": target_muscles[0] if target_muscles else "full_body",
                "sets": int(sets),
                "reps": reps,
                "rest_seconds": rest,
                "coaching_tip": "Maintain solid core engagement and controlled tempo on the eccentric phase.",
                "equipment_needed": "Dumbbells or Gym Machine" if location == 'gym' else "Bodyweight / Bands"
            }
        ],
        "cooldown": [
            {"exercise": "Static Hamstring and Chest Stretch", "duration": "3 minutes"}
        ],
        "estimated_duration_minutes": duration
    }
