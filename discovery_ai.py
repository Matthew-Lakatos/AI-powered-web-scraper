EXPANSIONS = {

    "ai": [
        "machine learning policy",
        "algorithm regulation",
        "AI governance",
        "AI ethics debate"
    ],

    "finance": [
        "stock market outlook",
        "crypto regulation",
        "global economic policy"
    ]
}


def expand_topic(topic):

    topic = topic.lower()

    expansions = []

    for k, vals in EXPANSIONS.items():

        if k in topic:

            expansions.extend(vals)

    expansions.append(topic)

    return list(set(expansions))
