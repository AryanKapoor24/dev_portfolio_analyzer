from unittest.mock import patch

import pytest

from backend.github_api import GitHubAuthError
from backend.portfolio_service import generate_portfolio


def repo(name):
    return {"name": name}


def analysis(name, commits):
    return {
        "name": name,
        "total_commits": commits,
        "stars": 0,
        "forks": 0,
        "activity_status": "Active",
        "language_bytes": {"Python": 100},
    }


def test_portfolio_contains_every_repo():
    repos = [repo("a"), repo("b")]

    def fake_analyze(token, r):
        return analysis(r["name"], 10)

    with patch("backend.portfolio_service.get_github_repos", return_value=repos), \
         patch("backend.portfolio_service.analyze_repos", side_effect=fake_analyze):

        portfolio = generate_portfolio("fake-token")

    assert [r["name"] for r in portfolio["repositories"]] == ["a", "b"]
    assert portfolio["developer_profile"]["total_commits"] == 20


def test_one_broken_repo_is_skipped_and_lists_stay_aligned():
    repos = [repo("good1"), repo("broken"), repo("good2")]

    def fake_analyze(token, r):
        if r["name"] == "broken":
            raise ValueError("unexpected data from GitHub")
        return analysis(r["name"], 5)

    with patch("backend.portfolio_service.get_github_repos", return_value=repos), \
         patch("backend.portfolio_service.analyze_repos", side_effect=fake_analyze):

        portfolio = generate_portfolio("fake-token")

    # The broken repo is dropped from BOTH lists, in the same position
    assert [r["name"] for r in portfolio["repositories"]] == ["good1", "good2"]
    assert [a["name"] for a in portfolio["analyzed_repositories"]] == ["good1", "good2"]
    assert portfolio["developer_profile"]["total_repositories"] == 2


def test_expired_token_stops_everything():
    # A dead token must reach app.py (to log the user out), not be skipped
    with patch("backend.portfolio_service.get_github_repos", return_value=[repo("a")]), \
         patch("backend.portfolio_service.analyze_repos", side_effect=GitHubAuthError("expired")):

        with pytest.raises(GitHubAuthError):
            generate_portfolio("fake-token")
