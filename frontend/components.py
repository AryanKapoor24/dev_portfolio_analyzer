from datetime import datetime, timezone
from html import escape

import altair as alt
import pandas as pd
import streamlit as st

from frontend.styles import CHART_BLUE, TEXT_MUTED, GRID_COLOR


GITHUB_ICON = (
    '<svg height="20" width="20" viewBox="0 0 16 16" aria-hidden="true">'
    '<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17'
    '.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94'
    '-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87'
    ' 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59'
    '.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27'
    '.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56'
    '.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01'
    ' 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z">'
    '</path></svg>'
)


# ==========================================
# Helpers
# ==========================================

def render_html(html):
    # Streamlit renders HTML through Markdown, where indented lines after a
    # blank line become a code block. Strip indentation and blank lines so
    # optional parts (e.g. an empty bio) can never break the layout.
    lines = [line.strip() for line in html.splitlines()]
    st.markdown(" ".join(line for line in lines if line), unsafe_allow_html=True)


def time_ago(iso_date):
    # "2026-10-01T12:00:00Z" -> "3 days ago"
    if not iso_date:
        return "—"

    if isinstance(iso_date, str):
        date = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    else:
        date = iso_date

    seconds = (datetime.now(timezone.utc) - date).total_seconds()

    for unit, size in (("year", 31536000), ("month", 2592000),
                       ("day", 86400), ("hour", 3600), ("minute", 60)):
        if seconds >= size:
            count = int(seconds // size)
            return f"{count} {unit}{'s' if count > 1 else ''} ago"

    return "just now"


def build_repo_table(repos, analyzed_repos):
    # One row per repository, combining GitHub data and our analysis.
    # analyzed_repos is built in the same order as repos.
    rows = []

    for position, (repo, analysis) in enumerate(zip(repos, analyzed_repos)):
        rows.append({
            "_position": position,
            "Repository": repo["name"],
            "Language": analysis["most_used_language"],
            "Commits": analysis["total_commits"],
            "Commits (30d)": analysis["commit_frequency"],
            "Stars": analysis["stars"],
            "Forks": analysis["forks"],
            "Status": analysis["activity_status"],
            "README": analysis["readme_status"],
            "Updated": pd.to_datetime(repo["updated_at"]),
            "Link": repo["html_url"],
        })

    return pd.DataFrame(rows)


def horizontal_bar_chart(df, label_field, value_field, value_title, value_format):
    # Single-series sorted bar chart: one hue, thin bars, value labels at bar end
    height = max(len(df) * 34, 120)

    base = alt.Chart(df).encode(
        y=alt.Y(
            f"{label_field}:N",
            sort=df[label_field].tolist(),
            title=None,
            axis=alt.Axis(labelLimit=180, labelColor="#c9d1d9", ticks=False, domain=False),
        ),
        x=alt.X(
            f"{value_field}:Q",
            title=None,
            # Headroom so the value label after the longest bar isn't clipped
            scale=alt.Scale(domain=[0, float(df[value_field].max()) * 1.2], nice=False),
            axis=alt.Axis(grid=True, gridColor=GRID_COLOR, labels=False, ticks=False, domain=False),
        ),
        tooltip=[
            alt.Tooltip(f"{label_field}:N", title=label_field),
            alt.Tooltip(f"{value_field}:Q", title=value_title, format=value_format),
        ],
    )

    bars = base.mark_bar(
        color=CHART_BLUE,
        cornerRadiusEnd=4,
        size=18,
    )

    labels = base.mark_text(
        align="left",
        dx=6,
        color=TEXT_MUTED,
        fontSize=12,
    ).encode(
        text=alt.Text(f"{value_field}:Q", format=value_format)
    )

    return (bars + labels).properties(height=height)


# ==========================================
# Login Page
# ==========================================

def render_login(login_url):

    render_html(
        f"""
        <div class="hero">
            <h1>Turn your GitHub into a<br><span class="accent">developer portfolio</span></h1>
            <p>
                Connect your GitHub account to get an instant overview of your
                repositories, languages, commit activity and project health.
            </p>
            <a class="github-btn" href="{escape(login_url)}" target="_self">
                {GITHUB_ICON} Sign in with GitHub
            </a>
        </div>
        """
    )

    features = [
        ("📊", "Developer profile", "Commits, stars, forks and activity across all your repositories."),
        ("💻", "Language breakdown", "See which languages you actually write the most code in."),
        ("📁", "Repository insights", "Filter, sort and drill into any repository in seconds."),
    ]

    cols = st.columns(3, gap="medium")

    for col, (icon, title, text) in zip(cols, features):
        with col:
            render_html(
                f"""
                <div class="feature-card">
                    <div class="icon">{icon}</div>
                    <h4>{title}</h4>
                    <p>{text}</p>
                </div>
                """
            )

    st.markdown(
        '<p class="muted" style="text-align:center;margin-top:2rem;">'
        "Your GitHub data is only read, never changed. "
        "Your token is kept only for this browser session."
        "</p>",
        unsafe_allow_html=True,
    )


# ==========================================
# Sidebar
# ==========================================

def render_sidebar(user, on_refresh, on_logout):

    with st.sidebar:

        name = escape(user.get("name") or user["login"])
        login = escape(user["login"])

        bio = ""
        if user.get("bio"):
            bio = f'<div class="bio">{escape(user["bio"])}</div>'

        meta_parts = []
        if user.get("company"):
            meta_parts.append(f"🏢 {escape(user['company'])}")
        if user.get("location"):
            meta_parts.append(f"📍 {escape(user['location'])}")
        meta = ""
        if meta_parts:
            meta = f'<div class="meta">{" · ".join(meta_parts)}</div>'

        render_html(
            f"""
            <div class="profile">
                <img src="{escape(user['avatar_url'])}" alt="avatar">
                <div class="name">{name}</div>
                <div class="login"><a href="{escape(user['html_url'])}" target="_blank">@{login}</a></div>
                {bio}
                {meta}
                <div class="stats">
                    <span><b>{user.get('followers', 0)}</b> followers</span>
                    <span><b>{user.get('following', 0)}</b> following</span>
                </div>
            </div>
            """
        )

        st.divider()

        st.link_button(
            "View GitHub profile",
            user["html_url"],
            icon=":material/open_in_new:",
            width="stretch",
        )

        st.button(
            "Refresh data",
            icon=":material/refresh:",
            on_click=on_refresh,
            width="stretch",
            help="Re-fetch your repositories from GitHub",
        )

        st.button(
            "Log out",
            icon=":material/logout:",
            on_click=on_logout,
            width="stretch",
        )


# ==========================================
# Header + KPIs
# ==========================================

def render_header(user, generated_at):

    first_name = (user.get("name") or user["login"]).split()[0]

    st.title(f"Welcome back, {first_name} 👋")

    st.caption(
        f"Portfolio analyzed {time_ago(generated_at)} · "
        "data refreshes automatically every 10 minutes"
    )


def render_kpis(developer_profile, table):

    total_repos = developer_profile["total_repositories"]
    active_repos = developer_profile["active_repositories"]

    recent_commits = int(table["Commits (30d)"].sum()) if not table.empty else 0

    kpis = [
        ("Repositories", total_repos, None),
        ("Total commits", f"{developer_profile['total_commits']:,}", None),
        ("Commits (30 days)", recent_commits, "Commits in the last 30 days, across all repositories"),
        ("Stars earned", developer_profile["total_stars"], None),
    ]

    # Horizontal container wraps the cards onto new rows on narrow screens
    with st.container(horizontal=True, gap="small"):
        for label, value, help_text in kpis:
            st.metric(label, value, help=help_text, border=True, width="stretch")

    st.caption(f"{active_repos} of {total_repos} repositories updated in the last 30 days")


# ==========================================
# Overview tab
# ==========================================

def render_overview(developer_profile, table):

    left, right = st.columns(2, gap="large")

    # ---------- Language distribution ----------
    with left:
        with st.container(border=True):

            st.subheader("Languages")

            distribution = developer_profile["total_distribution"]

            if distribution:
                top_language = max(distribution, key=distribution.get)
                st.caption(f"Share of code across all repositories · mostly **{top_language}**")
            else:
                st.caption("Share of code across all repositories")

            if distribution:
                lang_df = (
                    pd.DataFrame(distribution.items(), columns=["Language", "Share"])
                    .sort_values("Share", ascending=False)
                )

                # Keep the chart readable: top 7 + "Other"
                if len(lang_df) > 8:
                    other = lang_df.iloc[7:]["Share"].sum()
                    lang_df = pd.concat([
                        lang_df.iloc[:7],
                        pd.DataFrame([{"Language": "Other", "Share": other}]),
                    ])

                lang_df["Share"] = lang_df["Share"] / 100

                st.altair_chart(
                    horizontal_bar_chart(lang_df, "Language", "Share", "Share", ".1%"),
                    width="stretch",
                )
            else:
                st.info("No language data available yet.")

    # ---------- Most active repositories ----------
    with right:
        with st.container(border=True):

            st.subheader("Most active repositories")
            st.caption("Top 8 by total commits")

            top = table[table["Commits"] > 0].nlargest(8, "Commits")

            if not top.empty:
                st.altair_chart(
                    horizontal_bar_chart(top, "Repository", "Commits", "Commits", ",d"),
                    width="stretch",
                )
            else:
                st.info("No commits found yet.")

    # ---------- Portfolio health ----------
    with st.container(border=True):

        st.subheader("Portfolio health")
        st.caption("Quick wins that make your profile look better to others")

        total = len(table)

        if total == 0:
            st.info("No repositories to analyze yet.")
            return

        with_readme = int(table["README"].sum())
        active = int((table["Status"] == "Active").sum())
        starred = int((table["Stars"] > 0).sum())

        c1, c2, c3 = st.columns(3, gap="large")

        with c1:
            st.progress(with_readme / total, text=f"**README coverage** — {with_readme}/{total}")
            missing = table.loc[~table["README"], "Repository"].tolist()
            if missing:
                st.caption("Missing: " + ", ".join(missing[:5]) + (" …" if len(missing) > 5 else ""))

        with c2:
            st.progress(active / total, text=f"**Active in last 30 days** — {active}/{total}")

        with c3:
            st.progress(starred / total, text=f"**Repos with stars** — {starred}/{total}")


# ==========================================
# Repositories tab
# ==========================================

def render_repositories(repos, analyzed_repos, table):

    if table.empty:
        st.info("No repositories found on this account.")
        return

    # ---------- Filters (one row) ----------
    f1, f2, f3, f4 = st.columns([3, 2, 2, 2], vertical_alignment="bottom")

    with f1:
        search = st.text_input(
            "Search",
            placeholder="Search repositories…",
            label_visibility="collapsed",
        )

    with f2:
        languages = ["All languages"] + sorted(table["Language"].unique())
        language = st.selectbox("Language", languages, label_visibility="collapsed")

    with f3:
        status = st.selectbox(
            "Status",
            ["All statuses", "Active", "Inactive"],
            label_visibility="collapsed",
        )

    with f4:
        sort_by = st.selectbox(
            "Sort by",
            ["Recently updated", "Most commits", "Most stars", "Name"],
            label_visibility="collapsed",
        )

    filtered = table

    if search:
        filtered = filtered[filtered["Repository"].str.contains(search, case=False, regex=False)]

    if language != "All languages":
        filtered = filtered[filtered["Language"] == language]

    if status != "All statuses":
        filtered = filtered[filtered["Status"] == status]

    sort_columns = {
        "Recently updated": ("Updated", False),
        "Most commits": ("Commits", False),
        "Most stars": ("Stars", False),
        "Name": ("Repository", True),
    }
    column, ascending = sort_columns[sort_by]
    filtered = filtered.sort_values(column, ascending=ascending).reset_index(drop=True)

    st.caption(f"Showing {len(filtered)} of {len(table)} repositories · select rows to see details")

    # ---------- Table ----------
    # The key includes the filters, so a selection never points at the wrong
    # row after the table changes.
    max_commits = int(table["Commits"].max()) or 1

    event = st.dataframe(
        filtered,
        key=f"repo_table_{search}_{language}_{status}_{sort_by}",
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row",
        width="stretch",
        column_order=["Repository", "Language", "Commits", "Stars", "Status", "README", "Updated", "Link"],
        column_config={
            "Repository": st.column_config.TextColumn(width="medium"),
            "Commits": st.column_config.ProgressColumn(
                format="%d", min_value=0, max_value=max_commits, width="small",
            ),
            "Stars": st.column_config.NumberColumn(format="⭐ %d", width="small"),
            "Status": st.column_config.SelectboxColumn(
                options=["Active", "Inactive"], width="small",
            ),
            "README": st.column_config.CheckboxColumn(width="small"),
            "Updated": st.column_config.DatetimeColumn(format="distance", width="small"),
            "Link": st.column_config.LinkColumn(display_text="Open ↗", width="small"),
        },
    )

    selected_rows = event.selection.rows

    if not selected_rows:
        st.info("Select one or more repositories in the table to see their details.", icon=":material/touch_app:")
        return

    # ---------- Detail cards ----------
    st.subheader(f"Selected repositories ({len(selected_rows)})")

    # _position points back into repos / analyzed_repos
    positions = filtered.iloc[selected_rows]["_position"].tolist()

    cols = st.columns(2, gap="medium")

    for index, position in enumerate(positions):
        repo, analysis = repos[position], analyzed_repos[position]

        with cols[index % 2]:
            render_repo_card(repo, analysis)


def render_repo_card(repo, analysis):

    with st.container(border=True):

        st.markdown(f"### {repo['name']}")

        with st.container(horizontal=True, gap="small"):
            if analysis["activity_status"] == "Active":
                st.badge("Active", icon=":material/bolt:", color="green")
            else:
                st.badge("Inactive", icon=":material/bedtime:", color="gray")

            if analysis["most_used_language"] != "Unknown":
                st.badge(analysis["most_used_language"], color="blue")

            if repo.get("private"):
                st.badge("Private", icon=":material/lock:", color="orange")

            if repo.get("fork"):
                st.badge("Fork", icon=":material/fork_right:", color="violet")

            if not analysis["readme_status"]:
                st.badge("No README", icon=":material/warning:", color="yellow")

        st.write(repo["description"] or "_No description provided._")

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Commits", f"{analysis['total_commits']:,}")
        m2.metric("Last 30d", analysis["commit_frequency"])
        m3.metric("Stars", analysis["stars"])
        m4.metric("Forks", analysis["forks"])

        languages = analysis["languages"]

        if languages:
            st.markdown("**Languages**")
            top_languages = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:4]
            for language, percentage in top_languages:
                st.progress(percentage / 100, text=f"{language} · {percentage:.1f}%")

        st.caption(f"Updated {time_ago(repo['updated_at'])}")

        st.link_button(
            "Open on GitHub",
            repo["html_url"],
            icon=":material/open_in_new:",
            width="stretch",
        )
