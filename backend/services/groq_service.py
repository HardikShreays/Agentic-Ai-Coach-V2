from __future__ import annotations

import os
from typing import Any, Optional

from groq import Groq


def _get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    return Groq(api_key=api_key)


def _extract_text(resp: Any) -> str:
    """
    Best-effort extraction for Groq chat completion responses.
    """
    try:
        choices = getattr(resp, "choices", None) or []
        if not choices:
            return str(resp)
        msg = getattr(choices[0], "message", None)
        content = getattr(msg, "content", None)
        if isinstance(content, str):
            return content.strip()
    except Exception:
        pass
    return str(resp)


def call_groq_user_prompt(
    *,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float = 0.2,
) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return _extract_text(resp)


def call_groq_with_messages(
    *,
    model: str,
    system: Optional[str],
    messages: list[dict],
    max_tokens: int,
    temperature: float = 0.2,
) -> str:
    """
    Uses role-based messages. If `system` is provided, it is prepended as a `system` message.
    """
    client = _get_client()
    all_messages = list(messages)
    if system:
        all_messages = [{"role": "system", "content": system}] + all_messages

    resp = client.chat.completions.create(
        model=model,
        messages=all_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return _extract_text(resp)

