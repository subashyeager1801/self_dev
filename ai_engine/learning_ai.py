"""
Learning AI engine — Generates adaptive multi-week roadmaps and study recommendations.
"""
import json
import logging
from .client import chat_completion

logger = logging.getLogger(__name__)

ROADMAP_GENERATION_PROMPT = """You are a senior technical mentor and curriculum architect.
Create a high-impact, practical 4-to-6 week learning roadmap for: "{topic}".

User Target: {target_hours} total hours across the roadmap.
Category: {category}

Output format: Return STRICT VALID JSON matching this schema:
{{
  "title": "Title of curriculum",
  "weeks": [
    {{
      "week_number": 1,
      "week_title": "Core Foundations & Mental Model",
      "topics": ["Subtopic 1", "Subtopic 2", "Hands-on Exercise"],
      "estimated_hours": 10,
      "completed": false
    }},
    {{
      "week_number": 2,
      "week_title": "Intermediate Patterns & Practice",
      "topics": ["Subtopic 3", "Subtopic 4", "Mini Project"],
      "estimated_hours": 10,
      "completed": false
    }}
  ],
  "learning_advice": "1-2 sentences on how to master this subject effectively (e.g. active recall and coding every day)."
}}
"""


def generate_learning_roadmap(topic: str, category: str = "programming", target_hours: int = 40) -> dict:
    """Generate structured multi-week roadmap for a skill or subject."""
    prompt = ROADMAP_GENERATION_PROMPT.format(
        topic=topic,
        category=category,
        target_hours=target_hours
    )

    messages = [
        {"role": "system", "content": "You are a master educator. Always respond in strict JSON."},
        {"role": "user", "content": prompt}
    ]

    try:
        raw_response = chat_completion(messages, temperature=0.5, max_tokens=1200)
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
        logger.warning(f"AI roadmap generation failed: {e}")
        # Default structured fallback roadmap
        return {
            "title": f"{topic} Mastery Path",
            "weeks": [
                {
                    "week_number": 1,
                    "week_title": "Foundations & Core Principles",
                    "topics": ["Environment setup", "Core syntax & rules", "First basic exercise"],
                    "estimated_hours": max(5, int(target_hours / 4)),
                    "completed": False
                },
                {
                    "week_number": 2,
                    "week_title": "Data Structures & Application",
                    "topics": ["Key algorithms & patterns", "Practical problem solving", "Debugging techniques"],
                    "estimated_hours": max(5, int(target_hours / 4)),
                    "completed": False
                },
                {
                    "week_number": 3,
                    "week_title": "Intermediate Projects & Real World Logic",
                    "topics": ["Architecture patterns", "Building a mini-project", "Optimization"],
                    "estimated_hours": max(5, int(target_hours / 4)),
                    "completed": False
                },
                {
                    "week_number": 4,
                    "week_title": "Portfolio Project & Interview Questions",
                    "topics": ["Testing & edge cases", "Deploying / Showcasing", "Comprehensive review"],
                    "estimated_hours": max(5, int(target_hours / 4)),
                    "completed": False
                }
            ],
            "learning_advice": "Focus on daily 45-minute active coding sessions rather than passive video watching."
        }
