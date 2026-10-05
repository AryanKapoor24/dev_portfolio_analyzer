import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from backend.github_api import get_github_repos, request_timings
from backend.analyzer import analyze_repos, analyze_developer


# How many repositories to analyze at the same time
MAX_WORKERS = 8


def print_timing_report(total_seconds, repo_count):

    # Group calls by endpoint type: languages, commits, readme, repos
    by_endpoint = defaultdict(list)

    for url, seconds in request_timings:
        by_endpoint[url.rstrip("/").split("/")[-1]].append(seconds)

    print("\n===== GitHub timing report =====")
    print(f"Repositories: {repo_count}")
    print(f"API calls:    {len(request_timings)}")
    print(f"Total time:   {total_seconds:.2f}s")

    for endpoint, times in sorted(by_endpoint.items()):
        print(
            f"  {endpoint:<10} {len(times):>4} calls  "
            f"avg {sum(times) / len(times):.2f}s  "
            f"max {max(times):.2f}s"
        )

    print("Slowest calls:")

    for url, seconds in sorted(request_timings, key=lambda t: t[1], reverse=True)[:5]:
        print(f"  {seconds:.2f}s  {url}")

    print("================================\n")


def generate_portfolio(access_token):

    request_timings.clear()
    start = time.perf_counter()

    # Get all repositories from GitHub
    repos = get_github_repos(access_token)

    repos_seconds = time.perf_counter() - start
    print(f"Fetched repository list in {repos_seconds:.2f}s")

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

    print_timing_report(
        time.perf_counter() - start,
        len(repos)
    )

    # Return everything together
    return {
        "repositories": repos,
        "analyzed_repositories": analyzed_repos,
        "developer_profile": developer_profile
    }
