import streamlit as st
import requests


def get_github_login_url():
    client_id = st.secrets["GITHUB_CLIENT_ID"]

    # Set GITHUB_REDIRECT_URI in secrets when deployed
    # (e.g. https://your-app.streamlit.app)
    redirect_uri = st.secrets.get(
        "GITHUB_REDIRECT_URI",
        "http://localhost:8501"
    )

    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        "&scope=read:user%20repo"
    )

    return url


def exchange_code_for_token(code):
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": st.secrets["GITHUB_CLIENT_ID"],
            "client_secret": st.secrets["GITHUB_CLIENT_SECRET"],
            "code": code,
        },
        headers={
            "Accept": "application/json"
        },
    )

    return response.json()