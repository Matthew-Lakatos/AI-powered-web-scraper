"""
claim_extraction.py
-------------------
LLM-backed claim extraction using OpenAI gpt-4o-mini.

Fix
---
The original module instantiated `OpenAI(api_key=...)` at import time.
Because the OpenAI client raises OpenAIError immediately when no key is
set, *any* import of this module — even from code that never calls
extract_claims() — crashed the entire process.

The client is now created lazily inside _get_client() and only when
OPENAI_API_KEY is actually present.  If the key is absent the function
logs a warning and returns None gracefully, so the rest of the pipeline
continues without LLM claim extraction.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level sentinel — populated on first successful call.
_client = None


def _get_client():
    """
    Return a cached OpenAI client, or None if the API key is not set.

    The client is created at most once per process lifetime.
    No exception is raised if the key is absent — callers handle None.
    """
    global _client
    if _client is not None:
        return _client

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        logger.warning(
            "OPENAI_API_KEY is not set — claim extraction will be skipped. "
            "Set the environment variable to enable this feature."
        )
        return None

    # Import is deferred so that the openai package is only required
    # when the feature is actually used.
    from openai import OpenAI
    _client = OpenAI(api_key=api_key)
    return _client


_PROMPT_TEMPLATE = """\
Extract the following from the article text:

1. Main claim
2. Supporting evidence
3. Counterarguments

Article:
{text}
"""


def extract_claims(text: str) -> Optional[str]:
    """
    Use gpt-4o-mini to extract the main claim, supporting evidence, and
    counterarguments from *text*.

    Returns the model's response as a plain string, or None when:
      - *text* is empty
      - OPENAI_API_KEY is not configured
      - the API call fails for any reason

    The caller (analyzer.py) is expected to handle a None return.
    """
    if not text or not text.strip():
        return None

    client = _get_client()
    if client is None:
        return None

    prompt = _PROMPT_TEMPLATE.format(text=text[:3000])

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except Exception:
        logger.warning("extract_claims: OpenAI API call failed", exc_info=True)
        return None
