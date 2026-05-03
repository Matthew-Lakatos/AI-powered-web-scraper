"""
llm_query_expansion.py
----------------------
LLM-backed search query expansion using OpenAI gpt-4o-mini.

Fix
---
Same root cause as claim_extraction.py: the OpenAI client was
instantiated at module level, causing an immediate crash on import
whenever OPENAI_API_KEY was absent.

The client is now created lazily inside _get_client().  When the key is
missing, generate_queries() falls back to returning [topic] so
discovery_ai.build_queries() always gets a usable list and the
exploration loop keeps running without LLM expansion.
"""

import logging
import os
from typing import List, Optional

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    """
    Return a cached OpenAI client, or None if OPENAI_API_KEY is not set.
    Logs a warning once on the first missing-key call.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.warning(
            "OPENAI_API_KEY is not set — LLM query expansion will be skipped. "
            "Set the environment variable to enable this feature."
        )
        return None

    from openai import OpenAI
    _client = OpenAI(api_key=api_key)
    return _client


_PROMPT_TEMPLATE = """\
Generate 10 search engine queries related to:

{topic}

Include:
- policy debates
- economic impact
- criticism
- technological innovation
- future outlook

Return one query per line with no numbering or bullet points.
"""


def generate_queries(topic: str) -> List[str]:
    """
    Ask gpt-4o-mini to generate 10 diverse search queries for *topic*.

    Returns a list of query strings.  Falls back to [topic] when:
      - OPENAI_API_KEY is not configured
      - the API call fails for any reason

    This guarantees discovery_ai.build_queries() always receives at
    least one usable query regardless of LLM availability.
    """
    client = _get_client()
    if client is None:
        return [topic]

    prompt = _PROMPT_TEMPLATE.format(topic=topic)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        raw_lines = response.choices[0].message.content.split("\n")
        queries = [line.strip("- ").strip() for line in raw_lines if line.strip()]
        return queries if queries else [topic]
    except Exception:
        logger.warning(
            "generate_queries: OpenAI API call failed — falling back to bare topic",
            exc_info=True,
        )
        return [topic]
