# Manual check against the REAL GitHub API (not run by pytest/CI).
# Run from the project root:
#   $env:GITHUB_TOKEN = "your token"; python -m scripts.check_github
import os

from backend.github_api import get_repository_commits

access_token = os.environ["GITHUB_TOKEN"]
owner = "AryanKapoor24"
repo = "chrome_extension"

commits, total = get_repository_commits(
    access_token,
    owner,
    repo
)

print("Total commits:", total)
print("Newest commit:", commits[0]["commit"]["message"] if commits else None)
