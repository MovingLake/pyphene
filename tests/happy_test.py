import json
import time
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
    g.sleep_time_seconds = 0
    parsed = json.loads(json_str)
    g.from_json(parsed)
    g.run()

def some_fun(x, y, z):
    raise Exception("hello")

def some_fun_sleep_check_iterate(x, y, event):
    while True:
        if event.is_set():
            break
        time.sleep(0.1)

def test_exception():
    g = Graph()
    g.sleep_time_seconds = 0
    g.add_node("node1", [], some_fun)
    with pytest.raises(Exception):
        g.run()

def test_exception_short_circuit():
    g = Graph()
    g.sleep_time_seconds = 2
    g.add_node("node5", [], some_fun_sleep_check_iterate)
    g.add_node("node3", [], some_fun)
    g.add_node("node4", ["node5"], lambda x,y,z: [{"x": x["node5"][0]["x"]*5}] )
    g.add_node("node2", ["node3", "node4", "node5"], lambda x,y,z: [{"x": x["node4"][0]["x"]*5}])
    g.add_node("node1", ["node2"], lambda x,y,z: [{"x": x["node2"][0]["x"]*5}])
    with pytest.raises(Exception):
        g.run()

def test_manual_happy():
    g = Graph()
    g.sleep_time_seconds = 0
    g.add_node("node5", [], lambda inputs, state, event: [{"x": 5}])
    g.add_node("node3", [], lambda x,y,z: [{"x": 5}])
    g.add_node("node4", ["node5"], lambda x,y,z: [{"x": x["node5"][0]["x"]*5}] )
    g.add_node("node2", ["node3", "node4", "node5"], lambda x,y,z: [{"x": x["node4"][0]["x"]*5}])
    g.add_node("node1", ["node2"], lambda x,y,z: [{"x": x["node2"][0]["x"]*5}])
    out = g.run()
    assert out == {
        "node1": [{"x": 625}],
        "node2": [{"x": 125}],
        "node3": [{"x": 5}],
        "node4": [{"x": 25}],
        "node5": [{"x": 5}]
    }