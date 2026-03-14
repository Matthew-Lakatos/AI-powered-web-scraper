import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_queries(topic):

    prompt = f"""
Generate 10 diverse search queries related to:

{topic}

Include policy debates, criticism, innovation,
economic impact, and future outlook.
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        queries = response.choices[0].message.content.split("\n")

        return [q.strip("- ") for q in queries if q]

    except Exception:
        return [topic]
