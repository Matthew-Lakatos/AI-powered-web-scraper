from topic_expansion import expand_topic
from llm_query_expansion import generate_queries


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


def build_queries(topic):

    queries = []

    queries.extend(expand_topic(topic))

    queries.extend(generate_queries(topic))

    return list(set(queries))


def expand_topic(topic):

    topic = topic.lower()

    expansions = []

    for k, vals in EXPANSIONS.items():

        if k in topic:

            expansions.extend(vals)

    expansions.append(topic)

    return list(set(expansions))
