"""
Career AI engine — Skill gap matrix analyzer, roadmap prioritizer, and interview strategy planner.
"""
import json
import logging
from .client import chat_completion

logger = logging.getLogger(__name__)

CAREER_GAP_PROMPT = """You are a senior tech recruiter and engineering career strategist.
Analyze the user's career ambition and skill profile.

Target Role: {target_role}
Current Skills (Competent): {current_skills}
Skills Needing Work / In Progress: {skills_in_progress}

Output format: Return STRICT VALID JSON matching this schema:
{{
  "readiness_score": 65,
  "summary_verdict": "2-sentence objective assessment of their distance to being interview-ready",
  "skill_matrix": [
    {{"skill": "Python", "status": "proficient", "importance": "critical"}},
    {{"skill": "DSA", "status": "gap", "importance": "high"}},
    {{"skill": "System Design", "status": "gap", "importance": "medium"}}
  ],
  "top_priorities": [
    "1. Solve 40 LeetCode Medium problems covering Graphs, Trees, Dynamic Programming",
    "2. Build 1 full-stack production project featuring async background jobs and Redis caching",
    "3. Conduct 2 mock technical interviews on behavioral & architecture questions"
  ],
  "recommended_project_idea": "A high-concurrency microservice with rate limiting, caching, and CI/CD pipelines."
}}
"""


def analyze_career_path(target_role: str, current_skills: list, skills_in_progress: list) -> dict:
    """Analyze career readiness and output prioritized skill gap action items."""
    prompt = CAREER_GAP_PROMPT.format(
        target_role=target_role,
        current_skills=', '.join(current_skills) if current_skills else 'None specified',
        skills_in_progress=', '.join(skills_in_progress) if skills_in_progress else 'General industry skills'
    )

    messages = [
        {"role": "system", "content": "You are an expert career strategist and tech hiring manager. Always respond in strict JSON."},
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
        logger.warning(f"Career AI analysis failed: {e}")
        return {
            "readiness_score": 60,
            "summary_verdict": f"You have foundational skills for {target_role}. Focusing on core algorithm mastery and system architecture will quickly bridge the remaining gap.",
            "skill_matrix": [
                {"skill": s, "status": "proficient", "importance": "high"} for s in current_skills
            ] + [
                {"skill": s, "status": "gap", "importance": "critical"} for s in skills_in_progress
            ],
            "top_priorities": [
                "1. Strengthen core algorithmic problem solving",
                "2. Complete one comprehensive end-to-end portfolio project",
                "3. Refine technical resume and start active mock interviews"
            ],
            "recommended_project_idea": "A full-featured web platform with authentication, API rate-limiting, and unit test coverage."
        }
