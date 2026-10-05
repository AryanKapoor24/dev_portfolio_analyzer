import streamlit as st

from auth.github_oauth import (
    get_github_login_url,
    exchange_code_for_token
)

from backend.github_api import (
    get_github_user,
    get_github_repos,
    get_repository_languages,
    get_repository_commits
)

from backend.analyzer import (
    analyze_repos,
    analyze_developer
)


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="Developer Portfolio Analyzer",
    page_icon="💻",
    layout="wide"
)


# ==========================================
# Title
# ==========================================

st.title("Developer Portfolio Analyzer")


# ==========================================
# Handle GitHub OAuth Callback
# ==========================================

code = st.query_params.get("code")

if code and "github_token" not in st.session_state:

    token_data = exchange_code_for_token(code)

    if "access_token" in token_data:

        access_token = token_data["access_token"]

        st.session_state["github_token"] = access_token

        user = get_github_user(access_token)

        st.session_state["github_user"] = user

        st.query_params.clear()


# ==========================================
# Login Page
# ==========================================

if "github_token" not in st.session_state:

    st.subheader("Analyze your GitHub profile")

    st.write(
        "Connect your GitHub account to analyze "
        "your repositories and development activity."
    )

    login_url = get_github_login_url()

    st.markdown(
        f"""
        <a href="{login_url}" target="_self">
            <button style="
                padding: 10px 20px;
                font-size: 16px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
            ">
                Login with GitHub
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )


# ==========================================
# Logged-in User
# ==========================================

else:

    access_token = st.session_state["github_token"]

    user = st.session_state["github_user"]

    st.header(f"Welcome, {user['login']} 👋")


    # ======================================
    # User Profile
    # ======================================

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Public Repositories",
            user["public_repos"]
        )

    with col2:
        st.metric(
            "Followers",
            user["followers"]
        )

    with col3:
        st.metric(
            "Following",
            user["following"]
        )


    # ======================================
    # Get ALL Repositories
    # ======================================

    repos = get_github_repos(access_token)


    # ======================================
    # Analyze ALL Repositories
    # ======================================

    analyzed_repos = []

    for repo in repos:

        result = analyze_repos(
            access_token,
            repo
        )

        analyzed_repos.append(result)


    # ======================================
    # Developer Profile
    # ======================================

    developer_profile = analyze_developer(
        analyzed_repos
    )

    st.markdown("---")

    st.subheader("Developer Profile")


    # ======================================
    # Developer Metrics
    # ======================================

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Repositories",
            developer_profile["total_repositories"]
        )

    with col2:
        st.metric(
            "Total Commits",
            developer_profile["total_commits"]
        )

    with col3:
        st.metric(
            "Total Stars",
            developer_profile["total_stars"]
        )

    with col4:
        st.metric(
            "Total Forks",
            developer_profile["total_forks"]
        )

    with col5:
        st.metric(
            "Active Repositories",
            developer_profile["active_repositories"]
        )


    # ======================================
    # Language Distribution
    # ======================================

    st.subheader("Language Distribution")

    language_distribution = developer_profile[
        "total_distribution"
    ]

    if language_distribution:

        for language, percentage in language_distribution.items():

            st.write(
                f"**{language}: {percentage}%**"
            )

    else:

        st.write(
            "No language data available."
        )


    # ======================================
    # Repository Selection
    # ======================================

    st.markdown("---")

    st.subheader("Select Repositories to Analyze")

    repo_names = [
        repo["name"]
        for repo in repos
    ]

    st.multiselect(
        "Choose repositories",
        repo_names,
        key="selected_repos"
    )

    selected_repos = st.session_state["selected_repos"]


    # ======================================
    # Show Selected Repositories
    # ======================================

    if selected_repos:

        st.markdown("---")

        st.subheader("Selected Repositories")

        for repo in repos:

            if repo["name"] not in selected_repos:
                continue


            # ==================================
            # Repository Information
            # ==================================

            col1, col2 = st.columns([3, 1])

            with col1:

                st.subheader(
                    repo["name"]
                )

                if repo["description"]:

                    st.write(
                        repo["description"]
                    )

                else:

                    st.write(
                        "No description"
                    )


                # ----------------------------------
                # Languages
                # ----------------------------------

                st.write(
                    "💻 **Languages:**"
                )

                languages = get_repository_languages(
                    access_token,
                    repo["owner"]["login"],
                    repo["name"]
                )

                if languages:

                    for language, bytes_count in languages.items():

                        st.write(
                            f"- {language}: "
                            f"{bytes_count} bytes"
                        )

                else:

                    st.write(
                        "No language data available"
                    )


            # ==================================
            # Repository Statistics
            # ==================================

            with col2:

                st.write(
                    f"⭐ **Stars:** "
                    f"{repo['stargazers_count']}"
                )

                st.write(
                    f"🍴 **Forks:** "
                    f"{repo['forks_count']}"
                )

                st.link_button(
                    "View Repository",
                    repo["html_url"]
                )


            # ==================================
            # Commits
            # ==================================

            commits = get_repository_commits(
                access_token,
                repo["owner"]["login"],
                repo["name"]
            )

            st.write(
                f"📝 **Commits returned:** "
                f"{len(commits)}"
            )

            st.markdown("---")

    else:

        st.info(
            "Select one or more repositories "
            "to view their details."
        )