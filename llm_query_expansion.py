import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_queries(topic):

    prompt = f"""
Generate 10 search engine queries related to:

{topic}

Include:
- policy debates
- economic impact
- criticism
- technological innovation
- future outlook
"""

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        lines = response.choices[0].message.content.split("\n")

        queries = []

        for line in lines:
            line = line.strip("- ").strip()
            if line:
                queries.append(line)

        return queries

    except Exception:
        return [topic]
