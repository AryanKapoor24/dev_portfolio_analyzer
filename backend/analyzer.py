from backend.github_api import get_repository_commits

def analyze_commits(acess_token, owner, repo):

    total_commits= get_repository_commits(
        acess_token,
        owner,
        repo
    )
    return len(total_commits)


def analyze_dates(access_token, owner, repo):

    commits= get_repository_commits(
        acess_token, owner, repo
    )

    date =[]
    for i in range (len(commits)):
        date.append(commits[i]['commit']['author']['date'])

        
    max_date= max(date)

    return max_date



