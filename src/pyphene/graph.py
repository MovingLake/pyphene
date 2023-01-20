from typing import Any, Callable
from .node import Node
import logging
import threading

logging.basicConfig(level=logging.INFO)

log = logging.getLogger("graph")

def evaluate_json(json_eval: dict) -> None:
    def _evaluate_json(dep_inputs: dict[str, list[dict[str, Any]]], state: dict[str, Any]):
        return eval(json_eval)
    return _evaluate_json

class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.num_starter_nodes = 0
        self.outputs: dict[str, list[dict[str, Any]]] = {}
    
    def add_node(self, name: str, dependencies: list[str], fun: Callable) -> Node:
        if name in self.nodes:
            raise ValueError(f"Node {name} already exists")
        if "__init" not in self.nodes:
            self.nodes["__init"] = Node("__init")
        node = Node(name)
        self.nodes[node.name] = node
        if dependencies == []:
            self.num_starter_nodes += 1
            node.dependencies.append(self.nodes["__init"])
        
        # Create all dependencies.
        for dep in dependencies:
            node.dependencies.append(self.nodes[dep])
            self.nodes[dep].num_downstream += 1
        node.fun = fun
        return node
    
    def remove_node(self, name: str) -> None:
        if name not in self.nodes:
            raise ValueError(f"Node {name} does not exist")
        node = self.nodes[name]
        for dep in node.dependencies:
            dep.num_downstream -= 1
        del self.nodes[name]
        

    def from_json(self, input: dict) -> None:
        # Create all nodes without dependencies.
        nodes = input["nodes"]
        for name, node in nodes.items():
            n = Node(name)
            if "dependencies" not in node:
                self.num_starter_nodes += 1
            self.nodes[name] = n

        # Create an init node from which the graph starts.
        self.nodes["__init"] = Node("__init")

        # Create all dependencies.
        for node in self.nodes.values():
            if node.name == "__init":
                continue
            if "dependencies" not in nodes[node.name]:
                node.dependencies.append(self.nodes["__init"])
                continue
            for dep in nodes[node.name]["dependencies"]:
                node.dependencies.append(self.nodes[dep])
                self.nodes[dep].num_downstream += 1
            if "fun" in nodes[node.name]:
                node.fun = evaluate_json(nodes[node.name]["fun"])
    
    def run(self) -> dict[str, list[dict[str, Any]]]:
        # Run the graph.
        threads = []
        for node in self.nodes.values():
            if node.name == "__init":
                continue
            t = threading.Thread(target=node.listen, args=())
            t.start()
            threads.append(t)

        # Send enough sparks to start the graph.
        for _ in range(self.num_starter_nodes):
            self.nodes["__init"].output_queue.put([{"spark": "ignited"}])
        log.info("Sent spark to %d nodes", self.num_starter_nodes)
        for t in threads:
            t.join()
        
        # Check for exceptions.
        for node in self.nodes.values():
            if node.name == "__init":
                continue
            if node.exception is not None:
                raise node.exception

        # Get all outputs.
        for node in self.nodes.values():
            if node.name == "__init":
                continue
            self.outputs[node.name] = node.output_queue.get()
        log.info("Graph finished running.")
        return self.outputs
