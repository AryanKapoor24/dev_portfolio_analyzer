from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from backend.analyzer import (
    analyze_commit_frequency,
    analyze_developer,
    analyze_language,
    analyze_most_used_language,
    analyze_repo_activity,
    analyze_repos,
    analyze_total_language_percentage,
)


def iso_days_ago(days):
    # GitHub-style timestamp, e.g. "2026-11-01T10:00:00Z"
    date = datetime.now(timezone.utc) - timedelta(days=days)
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


def commit(days_ago):
    return {"commit": {"author": {"date": iso_days_ago(days_ago)}}}


# ==========================================
# Languages
# ==========================================

def test_language_bytes_become_percentages():
    assert analyze_language({"Python": 750, "CSS": 250}) == {"Python": 75.0, "CSS": 25.0}


def test_repo_without_languages_returns_empty():
    assert analyze_language({}) == {}


def test_most_used_language():
    assert analyze_most_used_language({"Python": 75.0, "CSS": 25.0}) == "Python"


def test_most_used_language_unknown_when_empty():
    assert analyze_most_used_language({}) == "Unknown"


def test_total_language_percentage_is_weighted_by_bytes():
    # A big Python repo should outweigh a tiny JavaScript repo
    repos = [
        {"language_bytes": {"Python": 900}},
        {"language_bytes": {"JavaScript": 100}},
    ]

    assert analyze_total_language_percentage(repos) == {"Python": 90.0, "JavaScript": 10.0}


def test_total_language_percentage_with_no_code():
    assert analyze_total_language_percentage([{"language_bytes": {}}]) == {}


# ==========================================
# Activity
# ==========================================

def test_commit_frequency_counts_only_last_30_days():
    commits = [commit(1), commit(10), commit(29), commit(31), commit(200)]

    assert analyze_commit_frequency(commits) == 3


def test_commit_frequency_with_no_commits():
    assert analyze_commit_frequency([]) == 0


def test_repo_updated_recently_is_active():
    assert analyze_repo_activity({"updated_at": iso_days_ago(5)}) == "Active"


def test_repo_not_updated_for_long_is_inactive():
    assert analyze_repo_activity({"updated_at": iso_days_ago(90)}) == "Inactive"


# ==========================================
# Whole developer profile
# ==========================================

def test_developer_profile_adds_up_all_repos():
    repos = [
        {"total_commits": 100, "stars": 3, "forks": 1,
         "activity_status": "Active", "language_bytes": {"Python": 800}},
        {"total_commits": 50, "stars": 2, "forks": 0,
         "activity_status": "Inactive", "language_bytes": {"Python": 200}},
    ]

    profile = analyze_developer(repos)

    assert profile == {
        "total_repositories": 2,
        "total_commits": 150,
        "total_stars": 5,
        "total_forks": 1,
        "active_repositories": 1,
        "total_distribution": {"Python": 100.0},
    }


def test_developer_profile_with_no_repos():
    profile = analyze_developer([])

    assert profile["total_repositories"] == 0
    assert profile["total_commits"] == 0
    assert profile["total_distribution"] == {}


# ==========================================
# One repository, with GitHub mocked
# ==========================================

def test_analyze_repos_combines_github_data():
    repo = {
        "name": "devfolio",
        "owner": {"login": "riya"},
        "updated_at": iso_days_ago(2),
        "stargazers_count": 4,
        "forks_count": 1,
    }

    # Replace the three GitHub calls with fake answers
    with patch("backend.analyzer.get_repository_languages", return_value={"Python": 300, "CSS": 100}), \
         patch("backend.analyzer.get_repository_commits", return_value=([commit(1), commit(60)], 250)), \
         patch("backend.analyzer.get_repository_readme", return_value={"content": "IyBEZXZGb2xpbw=="}):

        result = analyze_repos("fake-token", repo)

    assert result == {
        "name": "devfolio",
        "languages": {"Python": 75.0, "CSS": 25.0},
        "language_bytes": {"Python": 300, "CSS": 100},
        "most_used_language": "Python",
        "total_commits": 250,
        "commit_frequency": 1,
        "activity_status": "Active",
        "stars": 4,
        "forks": 1,
        "readme_status": True,
    }


def test_analyze_repos_without_readme():
    repo = {
        "name": "empty",
        "owner": {"login": "riya"},
        "updated_at": iso_days_ago(100),
        "stargazers_count": 0,
        "forks_count": 0,
    }

    # GitHub returns 404 for a missing README, which github_request turns into None
    with patch("backend.analyzer.get_repository_languages", return_value={}), \
         patch("backend.analyzer.get_repository_commits", return_value=([], 0)), \
         patch("backend.analyzer.get_repository_readme", return_value=None):

        result = analyze_repos("fake-token", repo)

    assert result["readme_status"] is False
    assert result["most_used_language"] == "Unknown"
    assert result["activity_status"] == "Inactive"
