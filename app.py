import streamlit as st

from auth.github_oauth import get_github_login_url, exchange_code_for_token
from backend.github_api import get_github_user

st.set_page_config(
    page_title="Developer Portfolio Analyzer",
    page_icon="🐙",
    layout="centered"
)

# -----------------------------
# Check if GitHub sent us a code
# -----------------------------

code = st.query_params.get("code")

if code:
    token_data = exchange_code_for_token(code)

    access_token = token_data["access_token"]

    user = get_github_user(access_token)

    st.write(user)


# -----------------------------
# Login UI
# -----------------------------

st.title("Developer Portfolio Analyzer")

st.write(
    "Analyze your GitHub profile and discover your developer strengths."
)

st.divider()

st.subheader("Get started")

github_url = get_github_login_url()

st.link_button(
    "🐙 Continue with GitHub",
    github_url,
    use_container_width=True
)