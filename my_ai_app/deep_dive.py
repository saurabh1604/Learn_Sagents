import openai
import os
import streamlit as st

# Set your OpenAI API key here
# Remember to replace this with your actual key before running or securely load it via env variables if sharing
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

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
