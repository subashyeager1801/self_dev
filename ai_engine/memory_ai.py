"""
AI Memory Management engine.
Extracts user preferences, strengths, recurring habits, and insights to personalize future coaching.
"""
import json
import logging
from .client import chat_completion

logger = logging.getLogger(__name__)

MEMORY_EXTRACTION_PROMPT = """You are an AI memory synthesizer.
Read the user's message and recent interaction context to extract key long-term facts, preferences, strengths, or weaknesses.

User Message:
"{message}"

Current Existing Memories:
{existing_memories}

Extract up to 2 high-confidence, meaningful new memories that will help personalize future coaching.
Return STRICT JSON matching this schema:
{{
  "memories": [
    {{
      "category": "preference / strength / weakness / pattern / goal",
      "title": "Short title (e.g. Prefers Evening Gym Sessions)",
      "detail": "Detailed insight (e.g. Has more energy for compound lifts after 6 PM)",
      "confidence": "High / Medium"
    }}
  ]
}}
If there is nothing new or noteworthy to store, return {{"memories": []}}.
"""


def extract_memories(user_message: str, existing_memories: list) -> list:
    """Extract structured long-term memory items from user input."""
    prompt = MEMORY_EXTRACTION_PROMPT.format(
        message=user_message,
        existing_memories=json.dumps(existing_memories)
    )

    messages = [
        {"role": "system", "content": "You are an analytical memory synthesizer. Respond in strict JSON."},
        {"role": "user", "content": prompt}
    ]

    try:
        raw = chat_completion(messages, temperature=0.3, max_tokens=600)
        clean = raw.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        elif clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]
        clean = clean.strip()
        data = json.loads(clean)
        return data.get("memories", [])
    except Exception as e:
        logger.warning(f"Memory extraction skipped: {e}")
        return []
