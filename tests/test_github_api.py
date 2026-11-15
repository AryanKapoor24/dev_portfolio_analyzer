import json
from unittest.mock import patch

import pytest
import requests

from backend.github_api import (
    GitHubAuthError,
    get_github_repos,
    get_repository_commits,
    github_get,
)


def fake_response(status_code=200, body=None, link=None):
    # A real requests.Response, filled in by hand instead of by GitHub
    response = requests.Response()
    response.status_code = status_code
    response._content = json.dumps(body if body is not None else []).encode()
    response.url = "https://api.github.com/fake"

    if link:
        response.headers["Link"] = link

    return response


# ==========================================
# Status code handling
# ==========================================

def test_success_returns_the_response():
    with patch("backend.github_api.requests.get", return_value=fake_response(200, {"login": "riya"})):
        response = github_get("https://api.github.com/user", "fake-token")

    assert response.json() == {"login": "riya"}


def test_token_is_sent_as_bearer_header():
    with patch("backend.github_api.requests.get", return_value=fake_response(200)) as mock_get:
        github_get("https://api.github.com/user", "abc123")

    headers = mock_get.call_args.kwargs["headers"]
    assert headers["Authorization"] == "Bearer abc123"


@pytest.mark.parametrize("status_code", [404, 409])
def test_not_found_and_empty_repo_mean_no_data(status_code):
    with patch("backend.github_api.requests.get", return_value=fake_response(status_code)):
        assert github_get("https://api.github.com/x", "fake-token") is None


def test_401_raises_github_auth_error():
    with patch("backend.github_api.requests.get", return_value=fake_response(401)):
        with pytest.raises(GitHubAuthError):
            github_get("https://api.github.com/user", "expired-token")


@pytest.mark.parametrize("status_code", [403, 500])
def test_other_errors_raise(status_code):
    # 403 = rate limit, 500 = GitHub is down
    with patch("backend.github_api.requests.get", return_value=fake_response(status_code)):
        with pytest.raises(requests.HTTPError):
            github_get("https://api.github.com/user", "fake-token")


# ==========================================
# Pagination
# ==========================================

def test_repos_are_fetched_page_by_page_until_empty():
    pages = [
        fake_response(200, [{"name": f"repo{i}"} for i in range(100)]),
        fake_response(200, [{"name": f"repo{i}"} for i in range(100, 150)]),
        fake_response(200, []),
    ]

    with patch("backend.github_api.requests.get", side_effect=pages) as mock_get:
        repos = get_github_repos("fake-token")

    assert len(repos) == 150
    assert mock_get.call_count == 3
    assert [call.kwargs["params"]["page"] for call in mock_get.call_args_list] == [1, 2, 3]


def test_commit_total_is_read_from_the_last_page():
    # Page 1 is full and its Link header says the last page is 24.
    # Page 24 has 50 commits, so the total is (24 - 1) * 100 + 50 = 2350.
    link = (
        '<https://api.github.com/repos/riya/big/commits?per_page=100&page=2>; rel="next", '
        '<https://api.github.com/repos/riya/big/commits?per_page=100&page=24>; rel="last"'
    )
    first_page = fake_response(200, [{"sha": str(i)} for i in range(100)], link=link)
    last_page = fake_response(200, [{"sha": str(i)} for i in range(50)])

    with patch("backend.github_api.requests.get", side_effect=[first_page, last_page]) as mock_get:
        commits, total = get_repository_commits("fake-token", "riya", "big")

    assert total == 2350
    assert len(commits) == 100                       # newest 100, for 30-day activity
    assert mock_get.call_count == 2                  # never more than 2 calls
    assert mock_get.call_args_list[1].kwargs["params"]["page"] == 24


def test_small_repo_needs_one_call():
    # Fewer than 100 commits: no Link header, everything is on page 1
    page = fake_response(200, [{"sha": str(i)} for i in range(7)])

    with patch("backend.github_api.requests.get", return_value=page) as mock_get:
        commits, total = get_repository_commits("fake-token", "riya", "small")

    assert total == 7
    assert mock_get.call_count == 1


def test_empty_repo_has_no_commits():
    # GitHub answers 409 for a repo with no commits yet
    with patch("backend.github_api.requests.get", return_value=fake_response(409)):
        assert get_repository_commits("fake-token", "riya", "empty") == ([], 0)
