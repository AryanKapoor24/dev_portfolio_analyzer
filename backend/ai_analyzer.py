import json

from pydantic import BaseModel, Field, ValidationError

from backend.llm import ask_llm


# How many repositories to send to the AI (keeps the prompt small and fast)
MAX_REPOS = 25


# ==========================================
# 1. The shape of the AI's answer
# ==========================================

class DeveloperInsights(BaseModel):

    summary: str = Field(
        description="2-3 sentence professional summary of the developer"
    )

    strengths: list[str] = Field(
        description="3-5 strengths, each backed by evidence from their repositories"
    )

    improvement_areas: list[str] = Field(
        description="3-5 specific, actionable improvements"
    )

    suitable_roles: list[str] = Field(
        description="2-4 job roles that fit this developer"
    )


# ==========================================
# 2. The input: a compact version of the GitHub data
# ==========================================

def build_ai_input(portfolio):
    # Send only what the AI needs, not the raw GitHub JSON
    profile = portfolio["developer_profile"]

    repos = []

    for repo, analysis in zip(
        portfolio["repositories"],
        portfolio["analyzed_repositories"]
    ):
        repos.append({
            "name": repo["name"],
            "description": repo.get("description"),
            "is_fork": repo.get("fork", False),
            "languages_percent": analysis["languages"],
            "total_commits": analysis["total_commits"],
            "commits_last_30_days": analysis["commit_frequency"],
            "status": analysis["activity_status"],
            "stars": analysis["stars"],
            "forks": analysis["forks"],
            "has_readme": analysis["readme_status"],
        })

    # Most worked-on repositories first, then keep the top ones
    repos.sort(key=lambda r: r["total_commits"], reverse=True)

    return {
        "overview": {
            "total_repositories": profile["total_repositories"],
            "total_commits": profile["total_commits"],
            "total_stars": profile["total_stars"],
            "total_forks": profile["total_forks"],
            "active_repositories": profile["active_repositories"],
            "language_distribution_percent": profile["total_distribution"],
        },
        "repositories": repos[:MAX_REPOS],
    }


# ==========================================
# 3. The prompt
# ==========================================

SYSTEM_PROMPT = """
You are an experienced technical recruiter and senior software engineer.
You review a developer's GitHub data and write an honest, specific assessment.

Rules:
- Base everything ONLY on the data provided. Never invent technologies,
  projects or experience that the data does not show.
- Be specific: mention repository names and languages as evidence.
- Improvement areas must be practical actions (e.g. "add READMEs to X and Y").
- Reply with a single JSON object and nothing else.
"""


def build_prompt(ai_input):
    schema = json.dumps(DeveloperInsights.model_json_schema(), indent=2)
    data = json.dumps(ai_input, indent=2)

    return (
        "Analyze this developer's GitHub data.\n\n"
        f"Reply with JSON matching this schema:\n{schema}\n\n"
        f"GitHub data:\n{data}"
    )


# ==========================================
# 4. Ask the AI, validate, retry once
# ==========================================

def generate_developer_insights(portfolio):

    prompt = build_prompt(build_ai_input(portfolio))

    last_error = None

    for attempt in range(2):

        if last_error:
            # Second try: tell the AI exactly what was wrong last time
            prompt += (
                "\n\nYour previous reply was invalid:\n"
                f"{last_error}\n"
                "Reply again with valid JSON that matches the schema."
            )

        reply = ask_llm(SYSTEM_PROMPT, prompt, json_mode=True)

        try:
            # Pydantic checks every field exists and has the right type
            return DeveloperInsights.model_validate_json(reply)

        except ValidationError as error:
            last_error = error

    raise ValueError(
        f"The AI returned an invalid answer twice. Last error: {last_error}"
    )
