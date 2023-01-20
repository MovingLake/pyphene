import json
import pytest

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
        "node3": {
            "fun": "print('hello')"
        },
        "node4": {
            "dependencies": ["node5"]
        },
        "node5": {
            "fun": "5*6"
        }
    }
}
"""


def test_json_happy():
    g = Graph()
    parsed = json.loads(json_str)
    g.from_json(parsed)
    g.run()

def some_fun(x, y):
    raise Exception("hello")

def test_exception():
    g = Graph()
    g.add_node("node1", [], some_fun)
    with pytest.raises(Exception):
        g.run()

def test_manual_happy():
    g = Graph()
    g.add_node("node5", [], lambda inputs, state: [{"x": 5}])
    g.add_node("node3", [], lambda x,y: [{"x": 5}])
    g.add_node("node4", ["node5"], lambda x,y: [{"x": x["node5"][0]["x"]*5}] )
    g.add_node("node2", ["node3", "node4", "node5"], lambda x,y: [{"x": x["node4"][0]["x"]*5}])
    g.add_node("node1", ["node2"], lambda x,y: [{"x": x["node2"][0]["x"]*5}])
    out = g.run()
    assert out == {
        "node1": [{"x": 625}],
        "node2": [{"x": 125}],
        "node3": [{"x": 5}],
        "node4": [{"x": 25}],
        "node5": [{"x": 5}]
    }