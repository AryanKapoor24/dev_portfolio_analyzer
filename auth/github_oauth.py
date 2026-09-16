import streamlit as st
import requests


def get_github_login_url():
    client_id = st.secrets["GITHUB_CLIENT_ID"]

    url = (
        "https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        "&redirect_uri=http://localhost:8501"
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