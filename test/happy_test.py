
import json
from pyphene.src.graph import Graph

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

def test_happy():
    g = Graph()
    parsed = json.loads(json_str)
    g.from_json(parsed)
    g.run()