
"""
Week 10 - AI Integration helper.

This file is designed to:
- Stream responses (generator yielding chunks)
- Use an API key stored in Streamlit secrets: st.secrets["OPENAI_API_KEY"]
- Fail gracefully (important for marking: app should not crash)

IMPORTANT:
- If openai package is missing OR no key is set, we return a helpful message instead of crashing.
"""

from __future__ import annotations

from typing import Generator, List, Dict
import streamlit as st


def safe_error_message(err: Exception) -> str:
    """
    Convert technical exceptions to a clean message for the UI.
    This avoids scaring the user with long stack traces.
    """
    msg = str(err)

    # Common cases from Week 10 issues
    if "No secrets found" in msg or "secrets.toml" in msg:
        return (
            "AI error: No API key found.\n\n"
            "Fix: create `.streamlit/secrets.toml` and add:\n"
            'OPENAI_API_KEY = "sk-..."\n'
        )

    if "invalid_api_key" in msg or "Incorrect API key provided" in msg:
        return (
            "AI error: Your API key is invalid.\n\n"
            "Fix: generate a valid key, then update `.streamlit/secrets.toml`."
        )

    return f"AI error: {msg}"


def _domain_system_prompt(domain: str) -> str:
    """
    Domain-specific system prompt (Week 10 multi-domain requirement).
    """
    domain = domain.strip().lower()

    if domain == "cybersecurity":
        return (
            "You are a cybersecurity assistant. "
            "Be practical and structured. "
            "Use clear steps: triage, containment, eradication, recovery, prevention. "
            "Avoid hallucinating facts. If data is missing, say what you need."
        )

    if domain == "data science":
        return (
            "You are a data science assistant. "
            "Focus on data quality, governance, storage, feature/label sanity checks, and reproducibility. "
            "Give actionable recommendations, not vague advice."
        )

    # IT Operations
    return (
        "You are an IT operations assistant. "
        "Focus on incident/ticket triage, prioritization, SLA thinking, root cause reasoning, "
        "and operational best practices. Keep it actionable."
    )


def stream_chat_completion(
    domain: str,
    chat_history: List[Dict[str, str]],
    extra_context: str = "",
    model: str = "gpt-4o-mini",
) -> Generator[str, None, None]:
    """
    Stream a chat completion.

    chat_history format:
    [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."},
      ...
    ]

    extra_context:
    - optional DB context (incident/dataset/ticket) injected into the prompt.

    IMPORTANT:
    - We do NOT crash if openai is not installed or key missing.
    - We yield text progressively (streaming).
    """

    # 1) Read API key from secrets (recommended for Streamlit)
    api_key = None
    try:
        api_key = st.secrets.get("OPENAI_API_KEY", None)
    except Exception:
        api_key = None

    # 2) If no key -> return a helpful “setup” message (still satisfies UI demo)
    if not api_key:
        yield (
            "⚠️ AI is not configured yet (missing OPENAI_API_KEY).\n\n"
            "To enable Week 10 AI:\n"
            "1) Install package: `pip install openai`\n"
            "2) Create `.streamlit/secrets.toml` with:\n"
            '   OPENAI_API_KEY = "sk-..."\n'
        )
        return

    # 3) Import OpenAI only when we need it (so missing package doesn't crash app startup)
    try:
        from openai import OpenAI
    except Exception:
        yield (
            "⚠️ The `openai` package is not installed.\n\n"
            "Fix:\n"
            "- Run: `pip install openai`\n"
            "- And keep OPENAI_API_KEY in `.streamlit/secrets.toml`\n"
        )
        return

    client = OpenAI(api_key=api_key)

    system_prompt = _domain_system_prompt(domain)

    # Build messages
    messages = [{"role": "system", "content": system_prompt}]

    if extra_context and extra_context.strip():
        messages.append(
            {
                "role": "system",
                "content": (
                    "Here is extra context from the database (use it as facts):\n\n"
                    f"{extra_context.strip()}"
                ),
            }
        )

    # Add conversation history
    for m in chat_history:
        # We only accept roles: user/assistant
        role = m.get("role", "")
        content = m.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})

    # 4) Stream from OpenAI
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        temperature=0.3,  # low-ish to reduce hallucinations
    )

    for event in stream:
        delta = event.choices[0].delta
        if delta and getattr(delta, "content", None):
            yield delta.content
