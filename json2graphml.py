import json
import re

import networkx as nx
import matplotlib.pyplot as plt


def read_source(filename):
    with open(filename, 'r') as f:
        source_data = json.loads(f.read())

    return source_data


def create_graph(source, name):
    g = nx.DiGraph()

    for node in source:

        # add node to graph
        if node["type"] != "metadata":
            node_id = node["_id"]
            if node["type"] != "pipe":
                icon = "system"
            else:
                icon = "pipe"

            yfile_type = "nodegraphics"
            g.add_node(node_id, label=node_id, icon=icon)

            # create edges between pipes and systems
            if node["type"] == "pipe":
                to_node = node_id

                if "system" in node["source"]:
                    from_node = node["source"]["system"]
                    g.add_edge(from_node, to_node)

                elif "alternatives" in node["source"]:
                    from_node = node["source"]["alternatives"]["prod"]["system"]
                    g.add_edge(from_node, to_node)

#                elif node["source"]["type"] == "rest":
#                    from_node = node["source"]["system"]
#                    g.add_edge(from_node, to_node)

#                if node["source"]["type"] == "http_endpoint":
#                    from_node = node["source"]["type"]
#                    g.add_edge(from_node, to_node)

                elif node["source"]["type"] == "dataset":
                    from_node = node["source"]["dataset"]
                    g.add_edge(from_node, to_node)

                elif node["source"]["type"] == "merge":
                    sources = node["source"]["datasets"]
                    for s in sources:
                        from_node = re.split(' ', s)[0] # skip dataset aliases
                        g.add_edge(from_node, to_node)

                if "sink" in node:
                    if "system" in node["sink"]:
                        from_node = node_id
                        to_node = node["sink"]["system"]
                        g.add_edge(from_node, to_node)

                if "transform" in node:
                    if "rules" in node["transform"]:
                        default = node["transform"]["rules"]["default"]
                        item_to_find = "hops"
#                        print(default)
#                        item = find_in_nested_list(default, item_to_find)
#                        print(item)

    return g


def find_in_nested_list(nested_list, item):
    found_item = None
    for element in nested_list:
        if isinstance(element, list):
            if find_in_nested_list(element, item):
                found_item = element[0]
                return found_item
        elif element == item:
            found_item = element[1]
            return found_item
    return found_item


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
    json_source = read_source("./celsio-prod-clean_no-config-groups.json")
#    print(f"{json_source}")
    graph = create_graph(json_source, "Celsio")
#    show_graph(graph)
    serialize_graph(graph, filename="./graph.graphml")
