import time
import requests


# Timing of every GitHub call: (url, seconds).
# Filled by github_request, read by portfolio_service to print a summary.
request_timings = []


def github_request(url, access_token, params=None):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    start = time.perf_counter()

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    request_timings.append((url, time.perf_counter() - start))

    # 404 = not found (e.g. repo has no README)
    # 409 = repo is empty (e.g. no commits yet)
    # These mean "no data", not a real error.
    if response.status_code in (404, 409):
        return None

    # Any other error (bad token, rate limit, ...) is a real problem
    response.raise_for_status()

    return response.json()

def get_github_user(access_token):
    url=    "https://api.github.com/user"
    return github_request(url, access_token)

def get_github_repos(access_token):
    all_repos = []
    page = 1

    while True:
        url = "https://api.github.com/user/repos"

        repos = github_request(
            url,
            access_token,
            params={
                "page": page,
                "per_page": 100
            }
        )

        if not repos:
            break

        all_repos.extend(repos)
        page += 1

    return all_repos
    

def get_repository_languages(access_token, owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/languages"

    # No data -> empty dict
    return github_request(url, access_token) or {}


def get_repository_commits(access_token, owner, repo):

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    commits = github_request(
        url,
        access_token,
        params={
            "per_page": 100
        }
    )

    # Empty repo -> empty list
    return commits or []

def get_repository_readme(access_token, owner, repo):
    url= f"https://api.github.com/repos/{owner}/{repo}/readme"

    return github_request(url, access_token)
        