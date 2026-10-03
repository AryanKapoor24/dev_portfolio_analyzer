import requests



def github_request(url, access_token, params=None):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

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

    return github_request(url, access_token)
        

def get_repository_commits(access_token, owner, repo):
    all_commits = []
    page = 1

    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"

        commits = github_request(
            url,
            access_token,
            params={
                "page": page,
                "per_page": 100
            }
        )

        if not commits:
            break

        all_commits.extend(commits)
        page += 1

    return all_commits

def get_repository_readme(access_token, owner, repo):
    url= f"https://api.github.com/repos/{owner}/{repo}/readme"

    return github_request(url, access_token)
        