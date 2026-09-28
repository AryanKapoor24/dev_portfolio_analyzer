from backend.github_api import get_repository_commits

access_token = "YOUR_TOKEN"
owner = "AryanKapoor24"
repo = "chrome_extension"

commits = get_repository_commits(
    access_token,
    owner,
    repo
)

print(commits[0])