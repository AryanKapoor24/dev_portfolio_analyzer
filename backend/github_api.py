import requests


def get_github_user(access_token):
    response = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )

    return response.json()

def get_github_repos(access_token):
    repo = []
    page = 1

    while True:
        response = requests.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
            params={
                "page": page,
                "per_page": 100
            }
        )

        repos = response.json()

        if not repos:
            break

        repo.extend(repos)

        page += 1

    return repo
    

def get_repository_languages(access_token, owner, repo):

    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/languages",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )

    return response.json()

def get_repository_commits(access_token, owner, repo):

    all_commits = []
    page = 1

    while True:

        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/commits",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
            params={
                "page": page,
                "per_page": 100
            }
        )

        commits = response.json()

        if not commits:
            break

        all_commits.extend(commits)

        page += 1

    return all_commits

def get_repository_readme(access_token, owner, repo):
    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/readme",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        }
    )

    return response.json()