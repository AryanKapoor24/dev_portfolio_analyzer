from backend.github_api import get_repository_commits, get_repository_languages
from datetime import datetime , timedelta, timezone

def analyze_commits(acess_token, owner, repo):

    total_commits= get_repository_commits(
        acess_token,
        owner,
        repo
    )
    return len(total_commits)



def analyze_dates(access_token, owner, repo):

    commits= get_repository_commits(
        access_token, owner, repo
    )

    date =[]
    for i in range (len(commits)):
        date.append(commits[i]['commit']['author']['date'])

        
    max_date= max(date)

    commit_date = datetime.fromisoformat(
        max_date.replace('Z', '+00:00')
    )

    today = datetime.now()
    today = datetime.now(timezone.utc)

    thrity_days_ago = today - timedelta(days=30)

    if commit_date < thrity_days_ago:
        return "No commits in the last 30 days"

    else:
        return "Commits in the last 30 days"

    

def analyze_commit_freqency(access_token, owner, repo):

    commits= get_repository_commits(
        access_token, owner, repo
    )

    counter=0
    for i in range (len(commits)):
        date= commits[i]['commit']['author']['date']

        commit_date = datetime.fromisoformat(
            date.replace('Z', '+00:00'))

        today = datetime.now(timezone.utc)

        thirty_days_ago = today - timedelta(days=30)

        if commit_date >= thrity_days_ago:
            counter += 1
    return counter

def analyze_most_used_language(languages):
    highest_value = max(languages.values())

    for key, value in languages.items():
        if value == highest_value:
            return key




    




