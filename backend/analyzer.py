from backend.github_api import get_repository_commits, get_repository_languages, get_repository_readme
from datetime import datetime , timedelta, timezone
from collections import defaultdict

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

    if not languages:
        return "Unknown"

    highest_value = max(languages.values())

    for key, value in languages.items():
        if value == highest_value:
            return key

def analyze_language(access_token, owner, repo):

    languages = get_repository_languages(
        access_token,
        owner,
        repo
    )

    if not languages:
        return {}

    total_bytes = sum(languages.values())

    language_percentages = {}

    for language, bytes_count in languages.items():
        percentage = (bytes_count / total_bytes) * 100
        language_percentages[language] = round(percentage, 2)

    return language_percentages



def analyze_commit_frequency(access_token, owner, repo):
    commits = get_repository_commits(
        access_token,
        owner,
        repo
    )

    if not commits:
        return 0

    dates = []

    for commit in commits:
        date = commit["commit"]["author"]["date"]
        commit_date = datetime.fromisoformat(
            date.replace("Z", "+00:00")
        )
        dates.append(commit_date)

    oldest_date = min(dates)
    newest_date = max(dates)

    days = (newest_date - oldest_date).days

    if days < 30:
        return len(commits)

    months = days / 30

    return round(len(commits) / months, 2)


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

    if "content" in readme:
        return True

    return False



def analyze_repository(access_token, repo):

    languages = analyze_language(
        access_token,
        repo["owner"]["login"],
        repo["name"]
    )

    most_used_language = analyze_most_used_language(languages)

    commits = analyze_commits(
        access_token,
        repo["owner"]["login"],
        repo["name"]
    )

    commit_frequency = analyze_commit_frequency(
        access_token,
        repo["owner"]["login"],
        repo["name"]
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
        "most_used_language": most_used_language,
        "total_commits": commits,
        "commit_frequency": commit_frequency,
        "activity_status": activity_status,
        "stars": repo["stargazers_count"],
        "forks": repo["forks_count"],
        "readme_status": readme_status
    }

def analyze_total_language_percentage(access_token, repos):
        totals = defaultdict(int)

        for repo in repos:
               languages = get_repository_languages(
                    access_token,
                    repo["owner"]["login"],
                    repo["name"]
                )

               for language, bytes_count in languages.items():
                   totals[language] += bytes_count

        total_bytes = sum(totals.values())

        for key, value in totals.items():
            
            percentage = (value / total_bytes) * 100
            totals[key] = round(percentage, 2)

        return dict(totals)



def analyze_developer(access_token, repos, analyzed_repos):
    total_commits= 0
    total_stars =0
    total_forks =0
    active_repos = 0
    total_repos= len(analyzed_repos)
    total_percentage = analyze_total_language_percentage(access_token, repos)


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





               

        
     
        
        


        

        
                


