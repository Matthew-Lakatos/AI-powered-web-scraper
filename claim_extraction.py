import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_claims(text: str):

    if not text:
        return None

    prompt = f"""
Extract the following from the article text:

1. Main claim
2. Supporting evidence
3. Counterarguments

Article:
{text[:3000]}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    except Exception:
        return None
