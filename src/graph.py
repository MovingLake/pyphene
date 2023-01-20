from .node import Node
import logging
import threading

logging.basicConfig(level=logging.INFO)

log = logging.getLogger("graph")


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[str, Node] = {}
        self.num_starter_nodes = 0

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

    def run(self) -> None:
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
        log.info("Graph finished running.")
