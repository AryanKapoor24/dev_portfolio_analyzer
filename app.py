import streamlit as st

from auth.github_oauth import (
    get_github_login_url,
    exchange_code_for_token
)

from backend.github_api import (
    get_github_user,
    get_github_repos,
    get_repository_languages
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
    # Get Repositories
    # ======================================

    st.subheader("Your Repositories")

    repos = get_github_repos(access_token)

    st.write(
        f"Repositories returned: **{len(repos)}**"
    )


    # ======================================
    # Display Repositories
    # ======================================

    for repo in repos:

        # ----------------------------------
        # Get Repository Languages
        # ----------------------------------

        languages = get_repository_languages(
            access_token,
            repo["owner"]["login"],
            repo["name"]
        )


        st.markdown("---")

        col1, col2 = st.columns([3, 1])


        # ----------------------------------
        # Repository Information
        # ----------------------------------

        with col1:

            st.subheader(repo["name"])

            description = repo["description"]

            if description:

                st.write(description)

            else:

                st.write("No description")


            st.write("💻 **Languages:**")


            if languages:

                for language, bytes_count in languages.items():

                    st.write(
                        f"- {language}: {bytes_count} bytes"
                    )

            else:

                st.write("No language data available")


        # ----------------------------------
        # Repository Statistics
        # ----------------------------------

        with col2:

            st.write(
                f"⭐ **Stars:** {repo['stargazers_count']}"
            )

            st.write(
                f"🍴 **Forks:** {repo['forks_count']}"
            )

            st.link_button(
                "View Repository",
                repo["html_url"]
            )