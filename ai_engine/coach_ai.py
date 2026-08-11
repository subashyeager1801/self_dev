"""
AI Coach engine for generating daily plans, motivation, and habit recommendations.
"""
import json
import logging
from .client import chat_completion
from .prompts import DAILY_PLAN_PROMPT, MOTIVATION_PROMPT

logger = logging.getLogger(__name__)


def generate_daily_plan(user_context: dict) -> str:
    """Generate a structured, actionable daily plan for the user based on live metrics."""
    prompt = DAILY_PLAN_PROMPT.format(user_context=json.dumps(user_context, indent=2))

    messages = [
        {"role": "system", "content": "You are an elite personal life and fitness coach."},
        {"role": "user", "content": prompt}
    ]

    try:
        return chat_completion(messages, temperature=0.6, max_tokens=1000)
    except Exception as e:
        logger.error(f"Error generating AI daily plan: {e}")
        # Deterministic fallback
        return (
            "🎯 **Today's Priorities**:\n"
            "1. Complete your scheduled workout session with focus on form.\n"
            f"2. Hit your protein target ({user_context.get('protein_target', 100)}g) across balanced meals.\n"
            f"3. Drink {user_context.get('water_target', 3.0)}L of water throughout the day.\n"
            "4. Dedicate at least 45 minutes to high-value learning / career growth.\n"
            f"5. Wind down 30 minutes before bed to ensure {user_context.get('sleep_target', 7.5)} hours of recovery sleep."
        )


def generate_motivation(user_context: dict) -> str:
    """Generate punchy, authentic daily motivation tailored to recent performance."""
    prompt = MOTIVATION_PROMPT.format(user_context=json.dumps(user_context, indent=2))

    messages = [
        {"role": "system", "content": "You are a motivating, grounded life coach. Keep answers under 4 sentences."},
        {"role": "user", "content": prompt}
    ]

    try:
        return chat_completion(messages, temperature=0.7, max_tokens=300)
    except Exception as e:
        logger.error(f"Error generating AI motivation: {e}")
        return "Discipline isn't about feeling motivated every second — it's about honoring the commitments you made to yourself. Start with one small win today."
