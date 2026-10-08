from backend.github_api import get_repository_commits, get_repository_languages, get_repository_readme
from datetime import datetime , timedelta, timezone
from collections import defaultdict

def analyze_commits(commits):

    
    return len(commits)



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

    


def analyze_commit_frequency(commits):
    counter = 0

    today = datetime.now(timezone.utc)
    thirty_days_ago = today - timedelta(days=30)

    for i in range(len(commits)):
        date = commits[i]["commit"]["author"]["date"]

        commit_date = datetime.fromisoformat(
            date.replace("Z", "+00:00")
        )

        if commit_date >= thirty_days_ago:
            counter += 1

    return counter

def analyze_most_used_language(languages):

    if not languages:
        return "Unknown"

    highest_value = max(languages.values())

    for key, value in languages.items():
        if value == highest_value:
            return key

def analyze_language(languages):

    

    if not languages:
        return {}

    total_bytes = sum(languages.values())

    language_percentages = {}

    for language, bytes_count in languages.items():
        percentage = (bytes_count / total_bytes) * 100
        language_percentages[language] = round(percentage, 2)

    return language_percentages



def analyze_commit_frequency(commits):
    counter = 0

    today = datetime.now(timezone.utc)
    thirty_days_ago = today - timedelta(days=30)

    for commit in commits:
        date = commit["commit"]["author"]["date"]

        commit_date = datetime.fromisoformat(
            date.replace("Z", "+00:00")
        )

        if commit_date >= thirty_days_ago:
            counter += 1

    return counter


def analyze_repo_activity(repo):
    updated_at = repo["updated_at"]

    updated_date = datetime.fromisoformat(
        updated_at.replace("Z", "+00:00")
    )

    today = datetime.now(timezone.utc)

    days_since_update = (today - updated_date).days

    if days_since_update <= 30:
        return "Active"
    else:
        return "Inactive"


def analyze_repository_type(repos):
    original_repos = 0
    forked_repos = 0

    for repo in repos:
        if repo["fork"]:
            forked_repos += 1
        else:
            original_repos += 1

    return {
        "original": original_repos,
        "forked": forked_repos
    }

def analyze_repository_engagement(repos):
    total_stars = 0
    total_forks = 0

    for repo in repos:
        total_stars += repo["stargazers_count"]
        total_forks += repo["forks_count"]

    return {
        "total_stars": total_stars,
        "total_forks": total_forks
    }

    
def analyze_readme(access_token, owner, repo):
    readme = get_repository_readme(
        access_token,
        owner,
        repo
    )

    # readme is None when the repo has no README
    if readme and "content" in readme:
        return True

    return False



def analyze_repos(access_token, repo):

    raw_languages = get_repository_languages(
            access_token,
            repo["owner"]["login"],
            repo["name"]
        )
        

    languages = analyze_language(raw_languages)

    
    most_used_language = analyze_most_used_language(languages)

    commits = get_repository_commits(
        access_token,
        repo["owner"]["login"],
        repo["name"]
    )
    total_commits = analyze_commits(commits)

    commit_frequency = analyze_commit_frequency(
        commits
    )

    activity_status = analyze_repo_activity(repo)

    readme_status = analyze_readme(
        access_token,
        repo["owner"]["login"],
        repo["name"]
    )

    return {
        "name": repo["name"],
        "languages": languages,
        "language_bytes": raw_languages,
        "most_used_language": most_used_language,
        "total_commits": total_commits,
        "commit_frequency": commit_frequency,
        "activity_status": activity_status,
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "readme_status": readme_status
    }

def analyze_total_language_percentage(analyzed_repos):
    totals = defaultdict(int)

    for repo in analyzed_repos:
        languages = repo["language_bytes"]

        for language, bytes_count in languages.items():
            totals[language] += bytes_count

    total_bytes = sum(totals.values())

    if total_bytes == 0:
        return {}

    percentages = {}

    for language, bytes_count in totals.items():
        percentage = (bytes_count / total_bytes) * 100
        percentages[language] = round(percentage, 2)

    return percentages


def analyze_developer(analyzed_repos):
    total_commits= 0
    total_stars =0
    total_forks =0
    active_repos = 0
    total_repos= len(analyzed_repos)
    total_percentage = analyze_total_language_percentage(analyzed_repos)


    for repo in analyzed_repos:

        total_commits += repo["total_commits"]
        total_stars += repo["stars"]
        total_forks += repo["forks"]

        if repo["activity_status"] == "Active":
            active_repos += 1

    return{
        "total_repositories": total_repos,
        "total_commits": total_commits,
        "total_stars": total_stars,
        "total_forks": total_forks,
        "active_repositories": active_repos,
        "total_distribution": total_percentage 
    }





               

        
     
        
        


        

        
                


