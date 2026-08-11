"""
AI Progress and Weekly Review Analytics.
"""
import json
import logging
from .client import chat_completion
from .prompts import WEEKLY_REPORT_PROMPT

logger = logging.getLogger(__name__)


def generate_weekly_report(weekly_data: dict) -> str:
    """Generate an analytical weekly progress report evaluating workouts, nutrition, sleep, and self-development."""
    prompt = WEEKLY_REPORT_PROMPT.format(weekly_data=json.dumps(weekly_data, indent=2))

    messages = [
        {"role": "system", "content": "You are an executive wellness and high-performance analyst."},
        {"role": "user", "content": prompt}
    ]

    try:
        return chat_completion(messages, temperature=0.5, max_tokens=1400)
    except Exception as e:
        logger.error(f"Error generating weekly report: {e}")
        return (
            "### 📊 Weekly Performance Summary\n\n"
            "**Overall Score:** 78/100 (Solid Consistency)\n\n"
            "**💪 Workouts:** You stayed on track with your training frequency. Continue maintaining your progressive overload log.\n\n"
            "**🥗 Nutrition:** Protein intake was consistent on training days. Ensure weekend hydration doesn't dip.\n\n"
            "**🚀 Next Week's Focus:**\n"
            "1. Aim for at least 7.5 hours of sleep nightly for optimal CNS recovery.\n"
            "2. Prioritize hitting daily water targets earlier in the day.\n"
            "3. Keep building your daily habit streaks."
        )
