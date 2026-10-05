from concurrent.futures import ThreadPoolExecutor

from backend.github_api import get_github_repos
from backend.analyzer import analyze_repos, analyze_developer


# How many repositories to analyze at the same time
MAX_WORKERS = 8


def generate_portfolio(access_token):

    # Get all repositories from GitHub
    repos = get_github_repos(access_token)

    # Analyze repositories in parallel.
    # executor.map keeps results in the same order as repos,
    # which app.py relies on when zipping the two lists.
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:

        analyzed_repos = list(
            executor.map(
                lambda repo: analyze_repos(access_token, repo),
                repos
            )
        )

    # Generate overall developer profile
    developer_profile = analyze_developer(
        analyzed_repos
    )

    # Return everything together
    return {
        "repositories": repos,
        "analyzed_repositories": analyzed_repos,
        "developer_profile": developer_profile
    }
