import json
import os
import re

import networkx as nx
import matplotlib.pyplot as plt

import requests


def read_source(filename):
    with open(filename, 'r') as f:
        source_data = json.loads(f.read())

    return source_data


def connect_to_sesam(api_key: str, base_url: str, endpoint: str = "/api"):
    """
    Connects to Sesam's Instance API and returns the response from the specified endpoint.

    Parameters:
        api_key (str): Your Sesam API key.
        base_url (str): The base URL of your Sesam instance (e.g., https://your-instance.sesam.io).
        endpoint (str): The API endpoint to call (default is '/api').

    Returns:
        dict: JSON response from the Sesam API.
    """
    url = f"{base_url.rstrip('/')}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Sesam API: {e}")
        return None


def create_graph(source, name):
    g = nx.DiGraph()

    for node in source:

        config = node["config"]["effective"]
        graph = node["graph"]

        # add node to graph
        node_id = node["_id"]
        icon = config["type"]

        g.add_node(node_id, label=node_id, icon=icon)

        # create edges between pipes and systems
        if config["type"] == "pipe":
            to_node = node_id

            # main data flows
            for p in graph["upstream_pipes"]:
                from_node = p
                g.add_edge(from_node, to_node, type="main")

            # hops
            for p in graph["upstream_dependent_pipes"]:
                from_node = p
                g.add_edge(from_node, to_node, type="hops")

            # source systems
            if (config["source"]["type"] != "dataset"
                    and "system" in config["source"]
                    and config["source"]["system"] != "system:sesam-node"):
                from_node = f"{config["source"]["system"]} (source)"
                to_node = node_id
                g.add_node(from_node, label=from_node, icon="system", type="source")
                g.add_edge(from_node, to_node, type="main")

            # FIXME: conditional sources
            if ("alternatives" in config["source"]
                    and "prod" in config["source"]["alternatives"]
                    and "system" in config["source"]["alternatives"]["prod"]):
                from_node = f"{config["source"]["alternatives"]["prod"]["system"]} (source)"
                to_node = node_id
                g.add_node(from_node, label=from_node, icon="system", type="source")
                g.add_edge(from_node, to_node, type="main")


            # sink systems
            if (config["sink"]["type"] != "dataset"
                    and "system" in config["sink"]
                    and config["sink"]["system"] != "system:sesam-node"):
                from_node = node_id
                to_node = f"{config["sink"]["system"]} (target)"
                g.add_node(to_node, label=to_node, icon="system", type="target")
                g.add_edge(from_node, to_node, type="main")

            # rest transforms
            if "transform" in config:
                if "transforms" in config["transform"]:
                    transforms = config["transform"]["transforms"]
                    for t in transforms:
                        if "type" in t and t["type"] == "rest":
                            from_node = node_id
                            to_node = t["system"]
                            g.add_node(to_node, label=to_node, icon="system")
                            g.add_edge(from_node, to_node, type="transform")

    return g


def show_graph(g):
    pos = nx.spring_layout(g, seed=3068)
    nx.draw(g, pos=pos, with_labels=True)
    plt.show()


def serialize_graph(g, filename="./graph.graphml"):
    print(f'Exported {g} to {filename}')
#    nx.write_graphml_lxml(G=g, path=filename, prettyprint=True, named_key_ids=True)
    nx.write_graphml(g, filename)


if __name__ == "__main__":
#    json_source = read_source("/home/geir.hegsvold/.config/JetBrains/PyCharmCE2024.3/scratches/scratch.json")
#    json_source = read_source("./celsio-prod-clean_no-config-groups.json")

    # TODO: support cli params
    api_key = os.getenv("JWT")
    base_url = os.getenv("BASE_URL")
    json_source = connect_to_sesam(api_key, base_url, "/api/pipes?fields=config,graph")

#    print(f"{json_source}")

    graph = create_graph(json_source, "Sample")
#    show_graph(graph)
    serialize_graph(graph, filename="./graph.graphml")
