import streamlit as st
import sqlite3
import re
from streamlit_mermaid import st_mermaid
from db_setup import DB_PATH

def inject_custom_css():
    st.markdown("""
        <style>
        /* Cyberpunk Dark Mode Aesthetic */
        .stApp {
            background-color: #0b0f19;
            color: #d1d5db;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #38bdf8;
            font-family: 'Inter', sans-serif;
            font-weight: 700;
        }

        /* Card styling for feed items */
        /* Fade in animation for elements */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .stMarkdown, .stButton, .stMetric, .stExpander {
            animation: fadeIn 0.4s ease-out forwards;
        }

        /* Card styling for feed items */
        .stContainer {
            background-color: #1e293b !important;
            border-radius: 12px !important;
            border-left: 4px solid #38bdf8 !important;
            margin-bottom: 1.5rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5) !important;
            transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .stContainer:hover {
            transform: translateY(-4px) !important;
            box-shadow: 0 15px 25px -5px rgba(56, 189, 248, 0.3) !important;
        }

        .feed-title {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .feed-title a {
            color: #e0f2fe;
            text-decoration: none;
        }
        .feed-title a:hover {
            color: #7dd3fc;
            text-decoration: underline;
        }

        .feed-meta {
            font-size: 0.875rem;
            color: #94a3b8;
            margin-bottom: 1rem;
            font-family: 'SF Mono', Consolas, monospace;
        }

        .badge {
            display: inline-block;
            padding: 0.25em 0.6em;
            font-size: 75%;
            font-weight: 700;
            line-height: 1;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: 0.375rem;
            background-color: #3b82f6;
            color: white;
            margin-right: 0.5rem;
        }

        .badge-github { background-color: #10b981; }
        .badge-arxiv { background-color: #ef4444; }
        .badge-hn { background-color: #f59e0b; }

        /* Buttons */
        .stButton>button {
            background-color: #0ea5e9;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .stButton>button:hover {
            background-color: #0284c7;
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.6);
            transform: scale(1.02);
        }

        /* Chat Input Styling */
        .stChatInput {
            border-radius: 12px !important;
            border: 1px solid #38bdf8 !important;
        }

        /* Markdown Code Blocks */
        pre {
            background-color: #0f172a !important;
            border: 1px solid #334155;
            border-radius: 8px;
        }
        code {
            color: #86efac !important;
        }
        </style>
    """, unsafe_allow_html=True)

def render_feed_item(item):
    """Renders a single item from the feed as a styled card."""
    source_lower = item["source"].lower()
    badge_class = ""
    if "github" in source_lower: badge_class = "badge-github"
    elif "arxiv" in source_lower: badge_class = "badge-arxiv"
    elif "hacker news" in source_lower: badge_class = "badge-hn"

    # Properly escape the HTML summary so it's not interpreted as raw markdown code blocks
    import html
    summary = html.escape(item["summary"][:300]) + ('...' if len(item['summary']) > 300 else '')

    # To prevent markdown parsing issues inside raw HTML, we render the HTML explicitly
    # without indentation spaces triggering markdown code blocks.
    # Note: Streamlit's st.markdown can sometimes unexpectedly render indented text inside
    # HTML blocks as code blocks. We'll strip all leading whitespace from the HTML to be safe.
    # Since Streamlit's markdown parser converts newlines inside raw HTML blocks into `<br>`
    # or wraps them in code blocks sometimes, the best way to bypass the markdown engine entirely
    # is to construct the HTML as a single unbroken line string, or use st.html (if available) or `st.components.v1.html`
    # We will use st.html since it directly injects the HTML without markdown parsing.

    # To bypass Streamlit's aggressive markdown parsing inside HTML, we use st.components.v1.html
    # which isolates the HTML inside an iframe. However, since we want it to flow naturally,
    # another option is to just use st.markdown with a strict div wrapper and no empty lines.

    # To completely avoid Streamlit markdown engine's code block rendering bug,
    # we should never use raw HTML strings in st.markdown.
    # We instead render it safely using st.container and markdown primitives.
    with st.container(border=True):
        st.markdown(f"### <span class='badge {badge_class}'>[{item['source']}]</span> [{item['title']}]({item['url']})", unsafe_allow_html=True)

        meta = []
        if 'type' in item: meta.append(f"Type: {item['type']}")
        if 'stars' in item: meta.append(f"Stars: {item['stars']}")
        if 'published' in item: meta.append(f"Published: {item['published']}")

        st.caption(" | ".join(meta))
        st.write(summary)

def extract_mermaid(text):
    """Extracts mermaid code block from LLM output."""
    match = re.search(r'```mermaid(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def render_mermaid(code):
    """Renders a Mermaid.js diagram."""
    if code:
        # We need to sanitize potentially invalid mermaid from LLMs (e.g. quotes, brackets)
        # st_mermaid takes string input
        st_mermaid(code, height="400px")
    else:
        st.warning("No valid diagram code generated.")

def save_to_db(item):
    """Saves a feed item to the local SQLite DB."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if item["source"] == "ArXiv":
        cursor.execute("INSERT INTO saved_papers (title, url, summary) VALUES (?, ?, ?)",
                       (item["title"], item["url"], item["summary"]))
    elif item["source"] == "GitHub":
        cursor.execute("INSERT INTO saved_repos (name, url, description) VALUES (?, ?, ?)",
                       (item["title"], item["url"], item["summary"]))
    else:
        cursor.execute("INSERT INTO tracked_items (title, url, type) VALUES (?, ?, ?)",
                       (item["title"], item["url"], item["type"]))

    conn.commit()
    conn.close()
    st.toast(f"Saved: {item['title'][:30]}...")
