import sys

from backend.ai_analyzer import generate_developer_insights

# Windows terminals can't print some characters the AI uses (e.g. "‑")
sys.stdout.reconfigure(encoding="utf-8")


# Small fake portfolio in the same shape generate_portfolio() returns
def repo(name, description, fork=False):
    return {"name": name, "description": description, "fork": fork}


def analysis(languages, commits, recent, status, stars, forks, readme):
    return {
        "languages": languages,
        "total_commits": commits,
        "commit_frequency": recent,
        "activity_status": status,
        "stars": stars,
        "forks": forks,
        "readme_status": readme,
    }


portfolio = {
    "repositories": [
        repo("dev_portfolio_analyzer", "Turns GitHub data into a developer portfolio"),
        repo("todo-api", "REST API for todos with FastAPI and PostgreSQL"),
        repo("react-weather", "Weather app built with React"),
        repo("leetcode-solutions", None),
    ],
    "analyzed_repositories": [
        analysis({"Python": 95.0, "CSS": 5.0}, 120, 40, "Active", 3, 0, True),
        analysis({"Python": 88.0, "Dockerfile": 12.0}, 45, 0, "Inactive", 1, 0, True),
        analysis({"JavaScript": 70.0, "CSS": 20.0, "HTML": 10.0}, 30, 0, "Inactive", 0, 0, False),
        analysis({"C++": 100.0}, 210, 12, "Active", 0, 0, False),
    ],
    "developer_profile": {
        "total_repositories": 4,
        "total_commits": 405,
        "total_stars": 4,
        "total_forks": 0,
        "active_repositories": 2,
        "total_distribution": {"Python": 55.0, "C++": 30.0, "JavaScript": 10.0, "CSS": 5.0},
    },
}


insights = generate_developer_insights(portfolio)

print("SUMMARY:\n", insights.summary, "\n")
print("STRENGTHS:")
for item in insights.strengths:
    print(" -", item)
print("\nIMPROVEMENT AREAS:")
for item in insights.improvement_areas:
    print(" -", item)
print("\nSUITABLE ROLES:", ", ".join(insights.suitable_roles))
