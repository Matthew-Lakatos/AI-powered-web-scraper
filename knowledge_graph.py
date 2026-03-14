from collections import defaultdict

graph = defaultdict(set)


def add_relationship(topic, keyword):

    graph[topic].add(keyword)


def build_graph(topics, keywords):

    for t in topics:
        for k in keywords:
            add_relationship(t, k)


def get_graph():

    return {k: list(v) for k, v in graph.items()}
