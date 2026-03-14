BASE_EXPANSIONS = [
    "policy",
    "economics",
    "controversy",
    "innovation",
    "regulation",
    "ethics",
    "future outlook",
    "industry impact",
]


def expand_topic(topic):

    expansions = []

    for e in BASE_EXPANSIONS:
        expansions.append(f"{topic} {e}")

    expansions.append(topic)

    return list(set(expansions))
