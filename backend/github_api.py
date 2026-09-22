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
    response = requests.get(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )

    return response.json()

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

    response = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/commits",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/vnd.github+json",
        },
    )

    return response.json()

