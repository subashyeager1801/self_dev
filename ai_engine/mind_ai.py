"""
Mind & Journaling AI analysis engine.
Provides supportive, non-diagnostic reflection and identifies recurring productivity, stress, and consistency patterns.
"""
import json
import logging
from .client import chat_completion

logger = logging.getLogger(__name__)

MIND_REFLECTION_PROMPT = """You are a supportive, insightful personal growth reflection coach.
Analyze the user's daily journal entry and recent mental wellness check-in numbers.

User Check-In Metrics (1 to 10):
- Mood: {mood}/10
- Energy: {energy}/10
- Focus: {focus}/10
- Stress: {stress}/10
- Motivation: {motivation}/10

User Journal Entry:
"{entry_text}"

Guidelines:
- CRITICAL: Never diagnose any mental health condition, disorder, or clinical issue.
- Act as an empathetic, practical life coach who identifies daily patterns, procrastination triggers, and positive wins.
- Provide a brief, thoughtful reflection (2-3 paragraphs).
- Extract 1-3 concise recurring patterns or behavioral cues.
- Give 1 single high-leverage micro-action for tomorrow.

Return STRICT JSON matching this structure:
{{
  "reflection": "Thoughtful empathetic reflection on their entry...",
  "detected_patterns": ["e.g. Afternoon energy dip", "Phone distraction during deep work"],
  "actionable_advice": "Tomorrow, try a 45-minute distraction-free work sprint with phone in another room."
}}
"""


def analyze_journal_entry(entry_text: str, mood_metrics: dict) -> dict:
    """Analyze journal text and return supportive reflection, detected patterns, and actionable advice."""
    prompt = MIND_REFLECTION_PROMPT.format(
        mood=mood_metrics.get('mood', 7),
        energy=mood_metrics.get('energy', 7),
        focus=mood_metrics.get('focus', 7),
        stress=mood_metrics.get('stress', 4),
        motivation=mood_metrics.get('motivation', 7),
        entry_text=entry_text
    )

    messages = [
        {"role": "system", "content": "You are an empathetic, practical personal development reflection coach. Respond in valid JSON."},
        {"role": "user", "content": prompt}
    ]

    try:
        raw_response = chat_completion(messages, temperature=0.6, max_tokens=1000)
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        elif clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        return json.loads(clean_json)
    except Exception as e:
        logger.warning(f"AI journal analysis failed or fell back: {e}")
        return {
            "reflection": (
                "Taking time to put your thoughts on paper is a powerful habit in itself. "
                "Notice what drained your energy today and what gave you momentum. "
                "Protect your focus blocks tomorrow and remember consistency compounds."
            ),
            "detected_patterns": ["Need for dedicated recovery", "Desire for higher daily focus"],
            "actionable_advice": "Identify your single highest-priority task for tomorrow morning and start it within 30 minutes of waking up."
        }
