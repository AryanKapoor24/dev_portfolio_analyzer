import streamlit as st

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Developer Portfolio Analyzer",
    page_icon="🐙",
    layout="centered"
)

# -----------------------------
# Header
# -----------------------------
st.title("Developer Portfolio Analyzer")
st.write("Analyze your GitHub profile and discover your developer strengths.")

st.divider()

# -----------------------------
# GitHub Login
# -----------------------------

st.subheader("Get started")

# GitHub logo + login button
github_button = st.link_button(
    "🐙  Continue with GitHub",
    "#",
    use_container_width=True
)

st.caption("You'll be redirected to GitHub to securely authorize access.")

st.divider()

# -----------------------------
# Temporary UI
# -----------------------------
st.subheader("Preview")

user_text = st.text_input(
    "Enter some text:",
    placeholder="This will be replaced by your GitHub profile..."
)

slider_val = st.slider(
    "Select a value:",
    min_value=0,
    max_value=100,
    value=50
)

st.write(f"You entered: {user_text}")
st.write(f"Slider value: {slider_val}")

# -----------------------------
# Download
# -----------------------------
st.download_button(
    label="Download text",
    data=user_text,
    file_name="output.txt",
    mime="text/plain"
)