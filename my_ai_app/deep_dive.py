import openai
import os
import streamlit as st

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE"))

def chat_with_tutor(messages, context_title, context_summary):
    """Sends chat messages to OpenAI acting as an interactive tutor."""
    system_prompt = f"""
    You are an expert AI/ML interactive tutor for a senior engineer.
    You are currently discussing the paper/repo titled: '{context_title}'.
    Abstract/Summary context: {context_summary}

    Answer their questions, debate their points, and provide deep technical insights.
    Keep your responses highly technical but conversational. Use markdown and LaTeX where appropriate.
    """

    api_messages = [{"role": "system", "content": system_prompt}]
    # We map Streamlit's message format to OpenAI's
    for msg in messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=api_messages,
        temperature=0.7
    )
    return response.choices[0].message.content

@st.cache_data
def generate_weekly_synthesis(feeds):
    """Aggregates feed data and generates a high-level overview of the week's trends."""
    if not feeds:
        return "No data available to synthesize."

    # Extract just the titles and a tiny bit of summary from top 15 items to avoid blowing up context window
    context_items = []
    for item in feeds[:15]:
        context_items.append(f"Title: {item['title']}\nSource: {item['source']}\nAbstract: {item['summary'][:200]}...")

    context_text = "\n\n".join(context_items)

    prompt = f"""
    You are an expert AI/ML research analyst. Based on the following top trending papers and repositories from this week, provide a "Weekly Intelligence Synthesis".

    1. **The Big Picture**: Where is the research heading based on this data? (e.g., Focus on RAG, multi-agent frameworks, efficiency).
    2. **Key Breakthroughs**: Highlight 2-3 specific papers/repos from the list that seem the most novel or impactful.

    Keep it concise, highly professional, and inspiring. Use Markdown formatting.

    Data:
    {context_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a senior AI/ML strategy consultant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content

@st.cache_data
def generate_deep_dive(title, abstract_or_content):
    """Generates a deep dive summary focusing on novel contributions and advanced concepts."""
    prompt = f"""
    You are an expert AI/ML researcher with 11+ years of experience analyzing a new paper or framework titled: '{title}'.

    Content/Abstract: {abstract_or_content}

    Provide a "Deep Dive" that skips all introductory/basic material. Focus strictly on:
    1. The core novel contribution (what makes this different from existing SOTA).
    2. The architectural or algorithmic innovation.
    3. Potential failure modes or limitations not mentioned in the abstract.

    Keep it concise, highly technical, and formatted in Markdown.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a senior AI/ML research assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

@st.cache_data
def generate_concept_graph(title, abstract_or_content):
    """Extracts key concepts and relationships for a network graph."""
    prompt = f"""
    Analyze the following research paper/repo and extract 5 to 8 key concepts/entities and their relationships.
    Format the output STRICTLY as a JSON array of objects, with no markdown code block wrappers (e.g. no ```json), just the raw JSON text.
    Each object must have:
    - "source": string (the origin concept)
    - "target": string (the related concept)
    - "label": string (how they are related, max 3 words)

    Paper/Repo: '{title}'
    Content: {abstract_or_content}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a data extraction pipeline. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    # Try to parse the JSON
    import json
    try:
        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text)
    except Exception as e:
        print(f"Failed to parse concept graph JSON: {e}")
        return []

@st.cache_data
def generate_intuition(title, abstract_or_content):
    """Generates mathematical, conceptual, and visual intuition (Mermaid diagram)."""
    prompt = f"""
    You are an expert AI/ML researcher analyzing: '{title}'.

    Content/Abstract: {abstract_or_content}

    Provide an intuitive breakdown for a senior engineer.
    1. **Conceptual Intuition**: Explain the "aha!" moment or the mental model behind this approach.
    2. **Mathematical Intuition**: Describe the core objective function, loss, or key equation (use LaTeX formatting for math).
    3. **Visual Intuition**: Create a valid Mermaid.js graph code block (```mermaid ... ```) that visualizes the architecture, agent workflow, or data flow. Ensure the Mermaid code is structurally correct and uses valid syntax (e.g., avoid parentheses in node names unless quoted).
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a senior AI/ML research assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )
    return response.choices[0].message.content

@st.cache_data
def generate_code_scaffolding(title, abstract_or_content):
    """Generates advanced starter code for implementing the concept."""
    prompt = f"""
    You are a senior AI/ML engineer. Based on the paper/concept: '{title}'.

    Content: {abstract_or_content}

    Write advanced, production-ready Python scaffolding/starter code to implement the core idea of this paper.
    - Use modern libraries (e.g., PyTorch, LangChain, LangGraph, AutoGen, or raw asyncio depending on the concept).
    - Include type hints, docstrings, and modular design.
    - Focus on the *novel* part of the implementation (e.g., the custom router, the novel attention mechanism, the specific agent interaction loop).
    - Provide a completely runnable skeleton.

    Output strictly in markdown Python code blocks.
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an elite 10x AI/ML software engineer."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )
    return response.choices[0].message.content
