TARGETS = [
    {
        "name": "Apple",
        "type": "company",
        "industry": "technology",
        "keywords": ["Apple", "iPhone", "Tim Cook"]
    },
    {
        "name": "NVIDIA",
        "type": "company",
        "industry": "semiconductors",
        "keywords": ["NVIDIA", "GPU", "AI chips", "Jensen Huang"]
    },
    {
        "name": "Tesla",
        "type": "company",
        "industry": "automotive",
        "keywords": ["Tesla", "Elon Musk", "autonomous driving"]
    },
    {
        "name": "SpaceX",
        "type": "company",
        "industry": "aerospace",
        "keywords": ["SpaceX", "Starship", "Falcon 9"]
    },
    {
        "name": "Google",
        "type": "company",
        "industry": "technology",
        "keywords": ["Google", "Alphabet", "Gemini AI"]
    },
    {
        "name": "Microsoft",
        "type": "company",
        "industry": "technology",
        "keywords": ["Microsoft", "Azure", "OpenAI partnership"]
    },
    {
        "name": "OpenAI",
        "type": "technology",
        "industry": "AI",
        "keywords": ["OpenAI", "ChatGPT", "GPT models"]
    }
]


def detect_targets(text):

    text_lower = text.lower()
    matches = []

    for target in TARGETS:
        for keyword in target["keywords"]:
            if keyword.lower() in text_lower:
                matches.append(target["name"])
                break

    return matches
