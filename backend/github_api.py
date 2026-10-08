import time
import requests
from urllib.parse import urlparse, parse_qs


# Timing of every GitHub call: (url, seconds).
# Filled by github_get, read by portfolio_service to print a summary.
request_timings = []


def github_get(url, access_token, params=None):
    # Returns the full response (body + headers), or None for "no data"
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

    return response


def github_request(url, access_token, params=None):
    # Returns just the JSON body, or None for "no data"
    response = github_get(url, access_token, params)

    if response is None:
        return None

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


COMMITS_PER_PAGE = 100


def get_repository_commits(access_token, owner, repo):
    # Returns (newest commits, total commit count).
    #
    # Instead of downloading every page, we read the "last" page
    # number from GitHub's Link header:
    #   total = (last_page - 1) * 100 + commits on the last page
    # So any repo needs at most 2 calls.

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    first_page = github_get(
        url,
        access_token,
        params={
            "per_page": COMMITS_PER_PAGE
        }
    )

    # Empty repo -> no commits
    if first_page is None:
        return [], 0

    commits = first_page.json()

    last_link = first_page.links.get("last")

    # No "last" link -> everything fits on one page
    if not last_link:
        return commits, len(commits)

    # Read the page number out of the "last" link
    last_page_number = int(
        parse_qs(urlparse(last_link["url"]).query)["page"][0]
    )

    last_page = github_request(
        url,
        access_token,
        params={
            "per_page": COMMITS_PER_PAGE,
            "page": last_page_number
        }
    ) or []

    total = (last_page_number - 1) * COMMITS_PER_PAGE + len(last_page)

    return commits, total

def get_repository_readme(access_token, owner, repo):
    url= f"https://api.github.com/repos/{owner}/{repo}/readme"

    return github_request(url, access_token)
        