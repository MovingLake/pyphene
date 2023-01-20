import json

from src.pyphene.graph import Graph


json_str = """
{
    "nodes": {
        "node1": {
            "dependencies": ["node2"]
        },
        "node2": {
            "dependencies": ["node3", "node4", "node5"]
        },
        "node3": {},
        "node4": {
            "dependencies": ["node5"]
        },
        "node5": {
        }
    }
}
"""


def test_json_happy():
    g = Graph()
    parsed = json.loads(json_str)
    g.from_json(parsed)
    g.run()

def test_manual_happy():
    g = Graph()
    g.add_node("node5", [])
    g.add_node("node3", [])
    g.add_node("node4", ["node5"])
    g.add_node("node2", ["node3", "node4", "node5"])
    g.add_node("node1", ["node2"])
    g.run()
