import streamlit as st
from data_fetchers import fetch_all_feeds
from deep_dive import generate_deep_dive, generate_intuition, generate_code_scaffolding, chat_with_tutor, generate_weekly_synthesis, generate_concept_graph
from ui_components import inject_custom_css, render_feed_item, save_to_db, extract_mermaid, render_mermaid
import os

# Set API key globally for the app per user request
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY_HERE"
import sqlite3
import re
from db_setup import DB_PATH, init_db
from gamification import mark_as_read, get_user_stats
from streamlit_agraph import agraph, Node, Edge, Config

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
page = st.sidebar.radio("Navigation", ["Daily Feed", "My Workspace (Bookmarks)", "User Profile & Progress", "About"])

if page == "Daily Feed":
    st.title("🔥 The Cutting Edge: AI & Agents")
    st.markdown("Dynamic extraction from **ArXiv, GitHub, HN, and Top Labs**.")

    if "feeds" not in st.session_state:
        st.session_state.feeds = load_data()

    if "focus_mode" not in st.session_state:
        st.session_state.focus_mode = None

    if st.session_state.focus_mode is not None:
        # User clicked into a specific item to read
        item = st.session_state.focus_mode

        if st.button("🔙 Back to Feed"):
            st.session_state.focus_mode = None
            st.rerun()

        st.markdown(f"## {item['title']}")
        st.caption(f"Source: {item['source']} | [Original Link]({item['url']})")
        st.write("---")

        # Focus mode splits into two columns: Content (Left) and Interactive Tools (Right)
        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.subheader("Abstract / Summary")
            st.markdown(item["summary"])

            # Deep Dive Generation
            with st.spinner("Synthesizing Deep Dive..."):
                try:
                    summary = generate_deep_dive(item["title"], item["summary"])
                    st.markdown("### 🧬 Core Contributions")
                    st.markdown(summary)

                    st.markdown("---")
                    st.markdown("### 🧩 Conceptual & Mathematical Intuition")
                    intuition = generate_intuition(item["title"], item["summary"])

                    mermaid_code = extract_mermaid(intuition)
                    text_only = re.sub(r'```mermaid(.*?)```', '', intuition, flags=re.DOTALL)

                    st.markdown(text_only)

                    if mermaid_code:
                        st.markdown("### 📊 Architecture Visualization")
                        try:
                            render_mermaid(mermaid_code)
                        except Exception as e:
                            st.error("Failed to render diagram.")
                            st.code(mermaid_code, language="mermaid")

                    st.markdown("---")
                    st.markdown("### 🌐 Concept Network")
                    st.info("Dynamic relationship graph of key entities.")
                    try:
                        graph_data = generate_concept_graph(item["title"], item["summary"])
                        if graph_data:
                            nodes = []
                            edges = []
                            added_nodes = set()

                            for edge in graph_data:
                                source, target, label = edge.get("source"), edge.get("target"), edge.get("label")
                                if source and target:
                                    if source not in added_nodes:
                                        nodes.append(Node(id=source, label=source, size=25, shape="dot", color="#0ea5e9"))
                                        added_nodes.add(source)
                                    if target not in added_nodes:
                                        nodes.append(Node(id=target, label=target, size=20, shape="dot", color="#10b981"))
                                        added_nodes.add(target)

                                    edges.append(Edge(source=source, target=target, label=label))

                            config = Config(width=500, height=400, directed=True, physics=True, hierarchical=False)
                            agraph(nodes=nodes, edges=edges, config=config)
                        else:
                            st.caption("Not enough entities found for a concept graph.")
                    except Exception as e:
                        st.error(f"Error generating concept graph: {e}")

                    # Trigger XP logic for reading
                    xp_gained = mark_as_read(item["title"], item["url"], item["source"])
                    if xp_gained:
                        if xp_gained.get("level_up"):
                            st.balloons()
                            st.success(f"🎉 Level Up! You reached Level {xp_gained['new_level']}! (+{xp_gained['xp_gained']} XP)")
                        else:
                            st.toast(f"🧠 Knowledge Absorbed! (+{xp_gained['xp_gained']} XP)")

                except Exception as e:
                    st.error(f"Error calling OpenAI API: {e}")

            with st.expander("⚙️ Implementation Scaffolding"):
                with st.spinner("Generating Production-Ready Skeleton..."):
                    try:
                        code = generate_code_scaffolding(item["title"], item["summary"])
                        st.markdown("### 💻 Starter Code")
                        st.markdown(code)
                    except Exception as e:
                        st.error(f"Error calling OpenAI API: {e}")

        with right_col:
            st.subheader("💬 Interactive Tutor")
            st.info("Ask questions, debate methodology, or request simpler explanations.")

            # Initialize chat history for the current item
            chat_key = f"chat_{item['title']}"
            if chat_key not in st.session_state:
                st.session_state[chat_key] = [
                    {"role": "assistant", "content": "How can I help you understand this research better? Feel free to ask about the math, architecture, or implications."}
                ]

            # Display chat messages
            chat_container = st.container(height=500)
            with chat_container:
                for message in st.session_state[chat_key]:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            # Accept user input
            if prompt := st.chat_input("Ask the tutor...", key="chat_input"):
                # Add user message to state
                st.session_state[chat_key].append({"role": "user", "content": prompt})
                with chat_container:
                    with st.chat_message("user"):
                        st.markdown(prompt)

                # Get AI response
                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            try:
                                response = chat_with_tutor(st.session_state[chat_key], item["title"], item["summary"])
                                st.markdown(response)
                                # Append AI response to history
                                st.session_state[chat_key].append({"role": "assistant", "content": response})
                            except Exception as e:
                                st.error(f"Error communicating with Tutor API: {e}")
                                st.session_state[chat_key].pop() # Remove failed user message to try again

    else:
        # Standard Feed View

        # Weekly Overview Component
        with st.expander("🌍 Weekly Intelligence Synthesis (Big Picture)", expanded=True):
            if st.button("🔄 Synthesize Feed Data"):
                with st.spinner("Analyzing current feed trends..."):
                    try:
                        synthesis = generate_weekly_synthesis(st.session_state.feeds)
                        st.session_state["weekly_synthesis"] = synthesis
                    except Exception as e:
                        st.error(f"Error generating synthesis: {e}")

            if "weekly_synthesis" in st.session_state:
                st.markdown(st.session_state["weekly_synthesis"])
            else:
                st.info("Click 'Synthesize Feed Data' to get a high-level summary of where research is heading this week.")

        st.write("---")

        if st.button("🔄 Refresh Data Streams"):
            st.session_state.feeds = load_data()

        for idx, item in enumerate(st.session_state.feeds):
            render_feed_item(item)

            col1, col2, col3 = st.columns([2, 2, 8])

            with col1:
                if st.button("📌 Bookmark", key=f"save_{idx}"):
                    save_to_db(item)

            with col2:
                if item["source"] in ["ArXiv", "GitHub"]:
                    if st.button("📖 Focus Mode", key=f"focus_{idx}"):
                        st.session_state.focus_mode = item
                        st.rerun()

            st.write("---")

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

elif page == "User Profile & Progress":
    st.title("🏆 User Profile & Progress")
    st.markdown("Track your learning journey and mastery of AI/ML concepts.")

    stats = get_user_stats()
    if stats:
        st.write("---")

        col1, col2, col3 = st.columns(3)
        col1.metric("Current Level", f"Lvl {stats['level']} 🧠")
        col2.metric("Total XP", f"{stats['xp']} XP ⚡")

        # Calculate XP to next level
        xp_for_next = (stats['level'] * 100)
        progress = (stats['xp'] % 100) / 100.0

        col3.metric("Next Level At", f"{xp_for_next} XP 🎯")

        st.progress(progress, text=f"Progress to Level {stats['level'] + 1}")

        st.write("---")
        st.subheader("📚 Learning Statistics")
        st.markdown(f"- **Research Papers Absorbed:** {stats['papers_read']}")
        st.markdown(f"- **Repositories Explored:** {stats['repos_explored']}")

        st.subheader("🏅 Badges & Achievements")
        badges = []
        if stats['papers_read'] >= 1: badges.append("📖 Novice Researcher")
        if stats['papers_read'] >= 5: badges.append("🔬 Paper Wizard")
        if stats['repos_explored'] >= 1: badges.append("💻 Code Explorer")
        if stats['repos_explored'] >= 5: badges.append("🚀 Implementation Master")

        if badges:
            for badge in badges:
                st.markdown(f"### {badge}")
        else:
            st.info("Keep exploring the feed to unlock badges!")

    else:
        st.warning("Could not load user profile.")

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
