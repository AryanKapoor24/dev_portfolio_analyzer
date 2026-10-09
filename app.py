from datetime import datetime, timezone

import streamlit as st

from auth.github_oauth import (
    get_github_login_url,
    exchange_code_for_token
)

from backend.github_api import get_github_user

from backend.portfolio_service import generate_portfolio

from frontend.styles import inject_styles

from frontend.components import (
    build_repo_table,
    render_login,
    render_sidebar,
    render_header,
    render_kpis,
    render_overview,
    render_repositories
)


# ==========================================
# Page Configuration
# ==========================================

st.set_page_config(
    page_title="DevFolio · GitHub Portfolio Analyzer",
    page_icon="💻",
    layout="wide"
)

inject_styles()


# ==========================================
# Cached Portfolio
# ==========================================

# Cached by GitHub username, which stays the same across logins.
# The leading underscore tells Streamlit not to include the token
# in the cache key (a new token is issued on every login).
@st.cache_data(ttl=600, show_spinner=False)
def get_portfolio(username, _access_token):

    portfolio = generate_portfolio(_access_token)

    portfolio["generated_at"] = datetime.now(timezone.utc)

    return portfolio


# ==========================================
# Session Actions
# ==========================================

def logout():
    # Forget the token and user for this browser session
    for key in ("github_token", "github_user"):
        st.session_state.pop(key, None)

    st.query_params.clear()


def refresh_portfolio():
    # Drop only this user's cached portfolio, so it is fetched again
    user = st.session_state["github_user"]

    get_portfolio.clear(
        user["login"],
        st.session_state["github_token"]
    )


# ==========================================
# Handle GitHub OAuth Callback
# ==========================================

code = st.query_params.get("code")

if code and "github_token" not in st.session_state:

    with st.spinner("Signing you in…"):

        token_data = exchange_code_for_token(code)

    st.query_params.clear()

    if "access_token" in token_data:

        access_token = token_data["access_token"]

        st.session_state["github_token"] = access_token

        st.session_state["github_user"] = get_github_user(access_token)

    else:

        st.error(
            "GitHub sign-in failed or the link expired. Please try again.",
            icon=":material/error:"
        )


# ==========================================
# Login Page
# ==========================================

if "github_token" not in st.session_state:

    render_login(get_github_login_url())

    st.stop()


# ==========================================
# Dashboard
# ==========================================

access_token = st.session_state["github_token"]

user = st.session_state["github_user"]

render_sidebar(
    user,
    on_refresh=refresh_portfolio,
    on_logout=logout
)

with st.spinner("Analyzing your GitHub… this can take a few seconds the first time."):

    portfolio = get_portfolio(
        user["login"],
        access_token
    )

repos = portfolio["repositories"]

analyzed_repos = portfolio["analyzed_repositories"]

developer_profile = portfolio["developer_profile"]

table = build_repo_table(repos, analyzed_repos)


render_header(user, portfolio["generated_at"])

render_kpis(developer_profile, table)

overview_tab, repositories_tab = st.tabs([
    ":material/insights: Overview",
    ":material/folder: Repositories"
])

with overview_tab:
    render_overview(developer_profile, table)

with repositories_tab:
    render_repositories(repos, analyzed_repos, table)
