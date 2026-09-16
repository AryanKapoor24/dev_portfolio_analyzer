import streamlit as st

from auth.github_oauth import (
    get_github_login_url,
    exchange_code_for_token
)

from backend.github_api import (
    get_github_user,
    get_github_repos
)


st.title("Developer Portfolio Analyzer")

# -------------------------
# GitHub Login
# -------------------------

code = st.query_params.get("code")

if code and "github_token" not in st.session_state:

    token_data = exchange_code_for_token(code)

    if "access_token" in token_data:

        st.session_state["github_token"] = token_data["access_token"]

        user = get_github_user(
            st.session_state["github_token"]
        )

        st.session_state["github_user"] = user

        st.query_params.clear()


# -------------------------
# Logged-in User
# -------------------------

if "github_token" not in st.session_state:

    login_url = get_github_login_url()

    st.markdown(
        f'<a href="{login_url}" target="_self">'
        '<button>Login with GitHub</button>'
        '</a>',
        unsafe_allow_html=True
    )

else:

    access_token = st.session_state["github_token"]
    user = st.session_state["github_user"]

    st.header(f"Welcome, {user['login']} 👋")

    # -------------------------
    # Get repositories
    # -------------------------

    repos = get_github_repos(access_token)

    st.subheader("Your Repositories")

    st.write(f"Total repositories: **{len(repos)}**")

    # -------------------------
    # Display repositories
    # -------------------------

    for repo in repos:

        st.markdown("---")

        col1, col2 = st.columns([3, 1])

        with col1:

            st.subheader(repo["name"])

            if repo["description"]:
                st.write(repo["description"])
            else:
                st.write("No description")

            if repo["language"]:
                st.write(f"💻 **Language:** {repo['language']}")

        with col2:

            st.write(f"⭐ {repo['stargazers_count']}")
            st.write(f"🍴 {repo['forks_count']}")

            if repo["html_url"]:
                st.link_button(
                    "View Repository",
                    repo["html_url"]
                )