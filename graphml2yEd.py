import xml.etree.ElementTree as ET

# Input and output file paths
input_file = "./graph.graphml"
output_file = "./graph.yed.graphml"

# Register yEd yFiles namespace
yfiles_ns = "http://www.yworks.com/xml/graphml"
ET.register_namespace("y", yfiles_ns)

tree = ET.parse(input_file)
root = tree.getroot()

# add key tag with yfiles.type="nodegraphics" to have yEd recognize node labels
key = ET.SubElement(root, "{http://graphml.graphdrawing.org/xmlns}key", attrib={"id":"d0", "for":"node", "yfiles.type":"nodegraphics"})

# Find the key for node labels (usually attr.name="label")
label_key = None
for key in root.findall("{http://graphml.graphdrawing.org/xmlns}key"):
    if key.attrib.get("attr.name") == "label" and key.attrib.get("for") == "node":
        label_key = key.attrib["id"]
        break

if not label_key:
    raise Exception("No node label key found in GraphML.")

for node in root.findall(".//{http://graphml.graphdrawing.org/xmlns}node"):
    label = None
    for data in node.findall("{http://graphml.graphdrawing.org/xmlns}data"):
        if data.attrib.get("key") == label_key:
            label = data.text
            break
    if label:
        # Remove old label data (optional)
        node.remove(data)
        # Add y:ShapeNode with y:NodeLabel
        y_data = ET.SubElement(node, "{http://graphml.graphdrawing.org/xmlns}data", key=label_key)
#        y_data.set("yfiles.type", "nodegraphics")
        svg_node = ET.SubElement(y_data, "{%s}SVGNode" % yfiles_ns)
        node_label = ET.SubElement(svg_node, "{%s}NodeLabel" % yfiles_ns)
        svg_node_properties = ET.SubElement(y_data, "{%s}SVGNodeProperties" % yfiles_ns, usingVisualBounds="true")
        node_label.text = label

tree.write(output_file, encoding="utf-8", xml_declaration=True)
print(f"yEd-compatible GraphML written to {output_file}")