from datetime import datetime, timezone

import streamlit as st

from auth.github_oauth import (
    get_github_login_url,
    exchange_code_for_token
)

from backend.github_api import get_github_user, GitHubAuthError

from backend.portfolio_service import (
    generate_portfolio,
    generate_ai_insights
)

from backend.llm import describe_ai_error

from frontend.styles import inject_styles

from frontend.components import (
    build_repo_table,
    render_login,
    render_sidebar,
    render_header,
    render_kpis,
    render_overview,
    render_repositories,
    render_ai_intro,
    render_ai_insights
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


# Cached per user AND per portfolio version: after "Refresh data" the
# portfolio gets a new generated_at, so the insights are regenerated too.
# _portfolio is not hashed (it is big); generated_at identifies it.
@st.cache_data(ttl=3600, show_spinner=False)
def get_ai_insights(username, generated_at, _portfolio):
    return generate_ai_insights(_portfolio)


# ==========================================
# Session Actions
# ==========================================

def logout():
    # Forget the token and user for this browser session
    for key in ("github_token", "github_user", "ai_requested"):
        st.session_state.pop(key, None)

    st.query_params.clear()


def refresh_portfolio():
    # Drop only this user's cached portfolio, so it is fetched again
    user = st.session_state["github_user"]

    get_portfolio.clear(
        user["login"],
        st.session_state["github_token"]
    )


def request_ai_insights():
    st.session_state["ai_requested"] = True


def regenerate_ai_insights(username, generated_at):
    # Drop the cached insights, so the next run asks the AI again
    get_ai_insights.clear(username, generated_at, None)


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

    # e.g. "Your GitHub session has expired" after an automatic logout
    login_message = st.session_state.pop("login_message", None)

    if login_message:
        st.warning(login_message, icon=":material/lock_clock:")

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

try:

    with st.spinner("Analyzing your GitHub… this can take a few seconds the first time."):

        portfolio = get_portfolio(
            user["login"],
            access_token
        )

except GitHubAuthError:
    # Token no longer works: sign out and send the user back to the login page
    logout()
    st.session_state["login_message"] = (
        "Your GitHub session has expired. Please sign in again."
    )
    st.rerun()

except Exception as error:
    # GitHub down, rate limit, no internet... show a message instead of a crash
    st.error(
        "Couldn't load your GitHub data right now. Please try again in a moment.",
        icon=":material/cloud_off:"
    )
    st.caption(f"Details: {error}")
    st.button("Try again", icon=":material/refresh:")
    st.stop()

repos = portfolio["repositories"]

analyzed_repos = portfolio["analyzed_repositories"]

developer_profile = portfolio["developer_profile"]

table = build_repo_table(repos, analyzed_repos)


render_header(user, portfolio["generated_at"])

render_kpis(developer_profile, table)

overview_tab, repositories_tab, ai_tab = st.tabs([
    ":material/insights: Overview",
    ":material/folder: Repositories",
    ":material/auto_awesome: AI Insights"
])

with overview_tab:
    render_overview(developer_profile, table)

with repositories_tab:
    render_repositories(repos, analyzed_repos, table)

with ai_tab:

    # The AI only runs after the user asks for it (it is slower and
    # uses the API quota), then stays cached.
    if not st.session_state.get("ai_requested"):

        render_ai_intro(
            on_generate=request_ai_insights,
            has_repositories=len(repos) > 0
        )

    else:

        try:
            with st.spinner("Generating AI insights… this takes a few seconds."):

                insights = get_ai_insights(
                    user["login"],
                    portfolio["generated_at"],
                    portfolio
                )

            render_ai_insights(
                insights,
                on_regenerate=lambda: regenerate_ai_insights(
                    user["login"],
                    portfolio["generated_at"]
                )
            )

        except Exception as error:
            # An AI problem only affects this tab, never the dashboard
            st.error(describe_ai_error(error), icon=":material/error:")

            st.button("Try again", icon=":material/refresh:")
