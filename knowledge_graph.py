import networkx as nx

graph = nx.Graph()


def add_entity(entity):

    graph.add_node(entity, type="entity")


def add_topic(topic):

    graph.add_node(topic, type="topic")


def add_narrative(narrative):

    graph.add_node(narrative, type="narrative")


def link_entity_topic(entity, topic):

    graph.add_edge(entity, topic, relation="discusses")


def link_topic_narrative(topic, narrative):

    graph.add_edge(topic, narrative, relation="forms")


def link_narrative_source(narrative, source):

    graph.add_edge(narrative, source, relation="reported_by")


def get_neighbors(node):

    return list(graph.neighbors(node))
