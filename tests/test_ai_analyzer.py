import json
from unittest.mock import patch

import pytest

from backend.ai_analyzer import MAX_REPOS, build_ai_input, generate_developer_insights


VALID_REPLY = json.dumps({
    "summary": "A Python developer focused on data tools.",
    "strengths": ["Consistent commits to devfolio"],
    "improvement_areas": ["Add READMEs to older projects"],
    "suitable_roles": ["Backend Developer"],
})

# "strengths" is missing, so Pydantic must reject it
INVALID_REPLY = json.dumps({"summary": "Incomplete answer"})


def make_portfolio(repo_count):
    repos = [{"name": f"repo{i}", "description": None} for i in range(repo_count)]

    analyses = [
        {
            "languages": {"Python": 100.0},
            "total_commits": i,
            "commit_frequency": 0,
            "activity_status": "Active",
            "stars": 0,
            "forks": 0,
            "readme_status": True,
        }
        for i in range(repo_count)
    ]

    return {
        "repositories": repos,
        "analyzed_repositories": analyses,
        "developer_profile": {
            "total_repositories": repo_count,
            "total_commits": sum(range(repo_count)),
            "total_stars": 0,
            "total_forks": 0,
            "active_repositories": repo_count,
            "total_distribution": {"Python": 100.0},
        },
    }


# ==========================================
# What is sent to the AI
# ==========================================

def test_ai_input_keeps_only_the_most_worked_on_repos():
    ai_input = build_ai_input(make_portfolio(40))

    commits = [r["total_commits"] for r in ai_input["repositories"]]

    assert len(commits) == MAX_REPOS
    assert commits == sorted(commits, reverse=True)
    assert commits[0] == 39


# ==========================================
# Validating the AI's answer (the LLM is mocked)
# ==========================================

def test_valid_reply_is_returned():
    with patch("backend.ai_analyzer.ask_llm", return_value=VALID_REPLY) as mock_llm:
        insights = generate_developer_insights(make_portfolio(3))

    assert insights.suitable_roles == ["Backend Developer"]
    assert mock_llm.call_count == 1


def test_invalid_reply_is_retried_with_the_error():
    with patch("backend.ai_analyzer.ask_llm", side_effect=[INVALID_REPLY, VALID_REPLY]) as mock_llm:
        insights = generate_developer_insights(make_portfolio(3))

    assert insights.summary.startswith("A Python developer")
    assert mock_llm.call_count == 2

    # The second prompt tells the AI what was wrong the first time
    second_prompt = mock_llm.call_args_list[1].args[1]
    assert "Your previous reply was invalid" in second_prompt


def test_two_invalid_replies_raise():
    with patch("backend.ai_analyzer.ask_llm", return_value=INVALID_REPLY):
        with pytest.raises(ValueError, match="invalid answer twice"):
            generate_developer_insights(make_portfolio(3))
