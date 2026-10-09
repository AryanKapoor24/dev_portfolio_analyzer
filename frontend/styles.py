import streamlit as st


# Chart colors (validated for the dark surface)
CHART_BLUE = "#3987e5"
TEXT_MUTED = "#8b949e"
GRID_COLOR = "#21262d"


CSS = """
<style>
/* Tighter top spacing */
.block-container {
    padding-top: 2.5rem;
    max-width: 1200px;
}

/* KPI cards: wrap instead of squeezing on narrow screens */
[data-testid="stMetric"] {
    min-width: 150px;
}

/* ---------- Login page ---------- */
.hero {
    text-align: center;
    padding: 4rem 1rem 2rem;
}
.hero h1 {
    font-size: 2.8rem;
    line-height: 1.15;
    margin-bottom: 0.75rem;
}
.hero .accent {
    background: linear-gradient(90deg, #58a6ff, #a371f7);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}
.hero p {
    color: #8b949e;
    font-size: 1.15rem;
    max-width: 560px;
    margin: 0 auto 2rem;
}
.github-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.8rem 1.6rem;
    background: #238636;
    color: #ffffff !important;
    border: 1px solid rgba(240, 246, 252, 0.1);
    border-radius: 8px;
    font-weight: 600;
    font-size: 1.05rem;
    text-decoration: none !important;
    transition: background 0.15s ease;
}
.github-btn:hover {
    background: #2ea043;
}
.github-btn svg {
    fill: currentColor;
}
.feature-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 1.25rem;
    height: 100%;
}
.feature-card .icon {
    font-size: 1.6rem;
}
.feature-card h4 {
    margin: 0.5rem 0 0.25rem;
    padding: 0;
}
.feature-card p {
    color: #8b949e;
    margin: 0;
    font-size: 0.95rem;
}

/* ---------- Sidebar profile ---------- */
.profile {
    text-align: center;
    padding-top: 0.5rem;
}
.profile img {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    border: 2px solid #30363d;
}
.profile .name {
    font-size: 1.25rem;
    font-weight: 700;
    margin-top: 0.6rem;
}
.profile .login a {
    color: #8b949e;
    text-decoration: none;
}
.profile .bio {
    color: #c9d1d9;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}
.profile .meta {
    color: #8b949e;
    font-size: 0.85rem;
    margin-top: 0.4rem;
}
.profile .stats {
    display: flex;
    justify-content: center;
    gap: 1.25rem;
    margin-top: 0.75rem;
    font-size: 0.9rem;
    color: #8b949e;
}
.profile .stats b {
    color: #e6edf3;
}

/* Muted helper text */
.muted {
    color: #8b949e;
    font-size: 0.9rem;
}
</style>
"""


def inject_styles():
    st.markdown(CSS, unsafe_allow_html=True)
