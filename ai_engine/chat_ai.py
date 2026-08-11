"""
Conversational AI Coach handler with live user context and safety filters.
"""
import json
import logging
from .client import chat_completion
from .prompts import COACH_SYSTEM_PROMPT
from .safety import sanitize_input, check_for_medical_red_flags, format_medical_warning

logger = logging.getLogger(__name__)


def get_chat_response(user_message: str, user_context: dict, message_history: list = None) -> str:
    """
    Generate an intelligent, personalized conversational response from the AI Life Coach.
    """
    clean_message = sanitize_input(user_message)

    # Check for medical emergencies
    if check_for_medical_red_flags(clean_message):
        return format_medical_warning()

    context_str = json.dumps(user_context, indent=2)

    system_instruction = f"{COACH_SYSTEM_PROMPT}\n\n### Current User Context:\n{context_str}"

    messages = [{"role": "system", "content": system_instruction}]

    # Add historical messages (limit to recent turns)
    if message_history:
        for msg in message_history[-10:]:
            role = "assistant" if msg.get("role") in ["assistant", "ai"] else "user"
            messages.append({"role": role, "content": msg.get("content", "")})

    messages.append({"role": "user", "content": clean_message})

    try:
        response = chat_completion(messages, temperature=0.7, max_tokens=1000)
        return response
    except Exception as e:
        logger.error(f"Chat completion error: {e}")
        return (
            "I encountered a temporary connection issue reaching the AI engine. "
            "In the meantime, remember your key priorities today: stay hydrated, hit your protein target, "
            "and complete your daily workout!"
        )
