import os
import streamlit as st
from google import genai
from google.genai import types
import json

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY_HERE"))
MODEL_FLASH = "gemini-2.5-flash"
MODEL_PRO = "gemini-2.5-pro"

def chat_with_tutor(messages, context_title, context_summary):
    """Sends chat messages to Gemini acting as an interactive tutor."""
    system_instruction = f"""
    You are an expert AI/ML interactive tutor for a senior engineer.
    You are currently discussing the paper/repo titled: '{context_title}'.
    Abstract/Summary context: {context_summary}

    Answer their questions, debate their points, and provide deep technical insights.
    Keep your responses highly technical but conversational. Use markdown and LaTeX where appropriate.
    """

    # We map Streamlit's message format to Gemini's
    history = []

    # All messages except the last one goes into history
    for msg in messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

    latest_user_message = messages[-1]["content"]

    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=history + [latest_user_message],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
    )
    return response.text

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
    Based on the following top trending papers and repositories from this week, provide a "Weekly Intelligence Synthesis".

    1. **The Big Picture**: Where is the research heading based on this data? (e.g., Focus on RAG, multi-agent frameworks, efficiency).
    2. **Key Breakthroughs**: Highlight 2-3 specific papers/repos from the list that seem the most novel or impactful.

    Keep it concise, highly professional, and inspiring. Use Markdown formatting.

    Data:
    {context_text}
    """

    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a senior AI/ML strategy consultant.",
            temperature=0.4,
        )
    )
    return response.text

@st.cache_data
def generate_deep_dive(title, abstract_or_content):
    """Generates a deep dive summary focusing on novel contributions and advanced concepts."""
    prompt = f"""
    Analyze a new paper or framework titled: '{title}'.

    Content/Abstract: {abstract_or_content}

    Provide a "Deep Dive" that skips all introductory/basic material. Focus strictly on:
    1. The core novel contribution (what makes this different from existing SOTA).
    2. The architectural or algorithmic innovation.
    3. Potential failure modes or limitations not mentioned in the abstract.

    Keep it concise, highly technical, and formatted in Markdown.
    """

    response = client.models.generate_content(
        model=MODEL_PRO, # Use Pro for deeper technical synthesis
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a senior AI/ML research assistant.",
            temperature=0.3,
        )
    )
    return response.text

@st.cache_data
def generate_concept_graph(title, abstract_or_content):
    """Extracts key concepts and relationships for a network graph."""
    prompt = f"""
    Analyze the following research paper/repo and extract 5 to 8 key concepts/entities and their relationships.

    Paper/Repo: '{title}'
    Content: {abstract_or_content}
    """

    # Define the schema for Gemini structured output
    schema = types.Schema(
        type=types.Type.ARRAY,
        items=types.Schema(
            type=types.Type.OBJECT,
            properties={
                "source": types.Schema(type=types.Type.STRING),
                "target": types.Schema(type=types.Type.STRING),
                "label": types.Schema(type=types.Type.STRING),
            },
            required=["source", "target", "label"],
        )
    )

    response = client.models.generate_content(
        model=MODEL_FLASH,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a data extraction pipeline.",
            temperature=0.1,
            response_mime_type="application/json",
            response_schema=schema,
        )
    )

    try:
        return json.loads(response.text)
    except Exception as e:
        print(f"Failed to parse concept graph JSON: {e}")
        return []

@st.cache_data
def generate_intuition(title, abstract_or_content):
    """Generates mathematical, conceptual, and visual intuition (Mermaid diagram)."""
    prompt = f"""
    Analyze: '{title}'.

    Content/Abstract: {abstract_or_content}

    Provide an intuitive breakdown for a senior engineer.
    1. **Conceptual Intuition**: Explain the "aha!" moment or the mental model behind this approach.
    2. **Mathematical Intuition**: Describe the core objective function, loss, or key equation (use LaTeX formatting for math).
    3. **Visual Intuition**: Create a valid Mermaid.js graph code block (```mermaid ... ```) that visualizes the architecture, agent workflow, or data flow. Ensure the Mermaid code is structurally correct and uses valid syntax (e.g., avoid parentheses in node names unless quoted).
    """

    response = client.models.generate_content(
        model=MODEL_PRO,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are a senior AI/ML research assistant.",
            temperature=0.4,
        )
    )
    return response.text

@st.cache_data
def generate_code_scaffolding(title, abstract_or_content):
    """Generates advanced starter code for implementing the concept."""
    prompt = f"""
    Based on the paper/concept: '{title}'.

    Content: {abstract_or_content}

    Write advanced, production-ready Python scaffolding/starter code to implement the core idea of this paper.
    - Use modern libraries (e.g., PyTorch, LangChain, LangGraph, AutoGen, or raw asyncio depending on the concept).
    - Include type hints, docstrings, and modular design.
    - Focus on the *novel* part of the implementation (e.g., the custom router, the novel attention mechanism, the specific agent interaction loop).
    - Provide a completely runnable skeleton.

    Output strictly in markdown Python code blocks.
    """

    response = client.models.generate_content(
        model=MODEL_PRO,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction="You are an elite 10x AI/ML software engineer.",
            temperature=0.2,
        )
    )
    return response.text
