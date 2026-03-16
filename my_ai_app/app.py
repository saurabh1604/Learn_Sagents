import streamlit as st
from data_fetchers import fetch_all_feeds
from deep_dive import generate_deep_dive, generate_intuition, generate_code_scaffolding
from ui_components import inject_custom_css, render_feed_item, save_to_db, extract_mermaid, render_mermaid
import sqlite3
import re
from db_setup import DB_PATH, init_db

# Configure page layout and tab title
st.set_page_config(page_title="AI/ML Agentic Explorer", layout="wide", page_icon="🤖")

# Initialize DB on startup
init_db()

# Inject our custom dark theme styling
inject_custom_css()

def load_data():
    """Fetches data and caches it."""
    with st.spinner("Initializing Data Streams..."):
        return fetch_all_feeds()

# Sidebar Navigation
st.sidebar.title("🧠 Neural Link")
page = st.sidebar.radio("Navigation", ["Daily Feed", "My Workspace (Bookmarks)", "About"])

if page == "Daily Feed":
    st.title("🔥 The Cutting Edge: AI & Agents")
    st.markdown("Dynamic extraction from **ArXiv, GitHub, HN, and Top Labs**.")

    if "feeds" not in st.session_state:
        st.session_state.feeds = load_data()

    if st.button("🔄 Refresh Data Streams"):
        st.session_state.feeds = load_data()

    for idx, item in enumerate(st.session_state.feeds):
        # We render the custom card using raw HTML, but then use Streamlit buttons
        # for interactions below the card.
        render_feed_item(item)

        col1, col2, col3, col4 = st.columns([2, 2, 2, 6])

        with col1:
            if st.button("📌 Bookmark", key=f"save_{idx}"):
                save_to_db(item)

        # Only show Deep Dive / Scaffolding for Papers and Repos
        if item["source"] in ["ArXiv", "GitHub"]:
            with col2:
                if st.button("🔬 Deep Dive", key=f"deep_{idx}"):
                    st.session_state[f"show_deep_{idx}"] = not st.session_state.get(f"show_deep_{idx}", False)
                    if st.session_state.get(f"show_deep_{idx}", False):
                        st.session_state[f"show_code_{idx}"] = False
            with col3:
                if st.button("⚙️ Scaffolding", key=f"code_{idx}"):
                    st.session_state[f"show_code_{idx}"] = not st.session_state.get(f"show_code_{idx}", False)
                    if st.session_state.get(f"show_code_{idx}", False):
                        st.session_state[f"show_deep_{idx}"] = False

        st.write("---")

        # Rendering Deep Dive (Includes Abstract, Intuition + Mermaid)
        if st.session_state.get(f"show_deep_{idx}", False):
            with st.expander("🔬 Advanced Analysis Panel", expanded=True):
                with st.spinner("Synthesizing Deep Dive..."):
                    try:
                        # 1. Summary
                    summary = generate_deep_dive(item["title"], item["summary"])
                    st.markdown("### 🧬 Core Contributions")
                    st.markdown(summary)

                    st.markdown("---")

                    # 2. Intuition & Visuals
                    st.markdown("### 🧩 Conceptual & Mathematical Intuition")
                    intuition = generate_intuition(item["title"], item["summary"])

                    # Separate out the mermaid diagram
                    mermaid_code = extract_mermaid(intuition)
                    text_only = re.sub(r'```mermaid(.*?)```', '', intuition, flags=re.DOTALL)

                    st.markdown(text_only)

                    if mermaid_code:
                        st.markdown("### 📊 Architecture Visualization")
                        try:
                            render_mermaid(mermaid_code)
                        except Exception as e:
                            st.error("Failed to render diagram due to complex LLM output syntax.")
                            st.code(mermaid_code, language="mermaid")
                    except Exception as e:
                        st.error(f"Error calling OpenAI API: {e}. Check your API Key.")

        # Rendering Code Scaffolding
        if st.session_state.get(f"show_code_{idx}", False):
            with st.expander("⚙️ Implementation Scaffolding", expanded=True):
                with st.spinner("Generating Production-Ready Skeleton..."):
                    try:
                        code = generate_code_scaffolding(item["title"], item["summary"])
                        st.markdown("### 💻 Starter Code")
                        st.markdown(code)
                    except Exception as e:
                        st.error(f"Error calling OpenAI API: {e}. Check your API Key.")

elif page == "My Workspace (Bookmarks)":
    st.title("📂 My Workspace")
    st.markdown("Saved papers, repositories, and tracked projects.")

    conn = sqlite3.connect(DB_PATH)

    st.subheader("📄 Saved Papers")
    papers = conn.execute("SELECT title, url, summary FROM saved_papers ORDER BY id DESC").fetchall()
    if papers:
        for p in papers:
            st.markdown(f"**[{p[0]}]({p[1]})**")
            st.caption(f"{p[2][:150]}...")
            st.write("---")
    else:
        st.info("No papers saved yet.")

    st.subheader("💻 Saved Repositories")
    repos = conn.execute("SELECT name, url, description FROM saved_repos ORDER BY id DESC").fetchall()
    if repos:
        for r in repos:
            st.markdown(f"**[{r[0]}]({r[1]})**")
            st.caption(f"{r[2]}")
            st.write("---")
    else:
        st.info("No repositories saved yet.")

    st.subheader("📰 Tracked Articles & Discussions")
    items = conn.execute("SELECT title, url, type FROM tracked_items ORDER BY id DESC").fetchall()
    if items:
        for i in items:
            st.markdown(f"**[{i[0]}]({i[1]})** - *{i[2]}*")
            st.write("---")
    else:
        st.info("No articles saved yet.")

    conn.close()

elif page == "About":
    st.title("About this Tool")
    st.markdown("""
    Built for Senior AI/ML Engineers (11+ YOE).

    This app bypasses the noise and introductory content, focusing purely on:
    - **Novel Architectures** (Agentic AI, Multi-Agent Systems, RAG).
    - **Mathematical Intuition** (Objectives, losses, formulations).
    - **Implementation Details** (Code scaffolding for immediate experimentation).

    Data is sourced directly via APIs from ArXiv, GitHub, Hacker News, and top industry research labs (OpenAI, DeepMind, Hugging Face).
    """)
