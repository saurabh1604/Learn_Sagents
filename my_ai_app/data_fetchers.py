import arxiv
import requests
import feedparser
from datetime import datetime, timedelta
import urllib.parse
from bs4 import BeautifulSoup

# --- ArXiv Fetcher ---
def fetch_arxiv_papers(max_results=10):
    """Fetches recent papers related to Agentic AI, Multi-Agent Systems, and RAG."""
    query = 'all:"Agentic AI" OR all:"Multi-Agent" OR all:"Retrieval Augmented Generation" OR all:"LLM Agents"'
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending
    )

    papers = []
    client = arxiv.Client()
    for result in client.results(search):
        papers.append({
            "title": result.title,
            "url": result.pdf_url,
            "summary": result.summary,
            "published": result.published.strftime("%Y-%m-%d"),
            "authors": [author.name for author in result.authors],
            "source": "ArXiv",
            "type": "Paper"
        })
    return papers

# --- GitHub Fetcher ---
def fetch_github_trending(language="python", since="weekly"):
    """Fetches trending AI/Agent repositories from GitHub.
       We'll simulate it by searching for recent highly-starred repos."""

    # Using the search API to find recent popular repos with 'agent' or 'llm'
    date_last_week = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = f"agent OR llm OR langgraph OR autogen in:name,description,readme language:{language} created:>{date_last_week}"
    url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&sort=stars&order=desc"

    headers = {"Accept": "application/vnd.github.v3+json"}
    response = requests.get(url, headers=headers)

    repos = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get("items", [])[:10]:
            repos.append({
                "title": item["full_name"],
                "url": item["html_url"],
                "summary": item["description"] or "No description provided.",
                "stars": item["stargazers_count"],
                "source": "GitHub",
                "type": "Repository"
            })
    return repos

# --- RSS Blog Fetcher ---
def fetch_industry_blogs():
    """Fetches latest posts from top AI research blogs."""
    feeds = [
        {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
        {"name": "Hugging Face", "url": "https://huggingface.co/blog/feed.xml"},
        {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml"}, # Deepmind sometimes has issues with direct RSS, but we try
        {"name": "Anthropic", "url": "https://www.anthropic.com/feed.xml"} # Placeholder for anthropic if available
    ]

    posts = []
    for feed in feeds:
        parsed_feed = feedparser.parse(feed["url"])
        for entry in parsed_feed.entries[:3]: # Get top 3 from each
            posts.append({
                "title": f"[{feed['name']}] {entry.title}",
                "url": entry.link,
                "summary": entry.get("summary", "")[:200] + "...",
                "published": entry.get("published", ""),
                "source": feed["name"],
                "type": "Blog Post"
            })
    return posts

# --- Hacker News Fetcher ---
def fetch_hn_discussions(query="LLM agent OR multi-agent", tags="story"):
    """Fetches relevant discussions from Hacker News using Algolia API."""
    url = f"http://hn.algolia.com/api/v1/search?query={urllib.parse.quote(query)}&tags={tags}&numericFilters=created_at_i>{int((datetime.now() - timedelta(days=7)).timestamp())}"

    response = requests.get(url)
    discussions = []

    if response.status_code == 200:
        data = response.json()
        for hit in data.get("hits", [])[:10]:
            discussions.append({
                "title": hit.get("title", ""),
                "url": hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                "summary": f"Score: {hit.get('points', 0)} | Comments: {hit.get('num_comments', 0)}",
                "source": "Hacker News",
                "type": "Discussion"
            })
    return discussions

def fetch_all_feeds():
    """Aggregates all feeds into a single list."""
    feeds = []
    try:
        feeds.extend(fetch_arxiv_papers(max_results=5))
    except Exception as e:
        print(f"Error fetching ArXiv: {e}")

    try:
        feeds.extend(fetch_github_trending())
    except Exception as e:
        print(f"Error fetching GitHub: {e}")

    try:
        feeds.extend(fetch_industry_blogs())
    except Exception as e:
        print(f"Error fetching Blogs: {e}")

    try:
        feeds.extend(fetch_hn_discussions())
    except Exception as e:
        print(f"Error fetching HN: {e}")

    return feeds

if __name__ == "__main__":
    feeds = fetch_all_feeds()
    for f in feeds:
        print(f"{f['source']} - {f['title']}")
