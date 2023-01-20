import queue
from typing import Any
import logging

log = logging.getLogger("node")


class Node:
    def __init__(self, name) -> None:
        self.name: str = name
        self.output_queue: queue.Queue = queue.Queue()
        self.dependencies: list[Node] = []
        self.num_downstream: int = 0
        self.state: dict[str, Any] = {}

    def run(self, dep_inputs: dict[str, list[dict[str, Any]]]) -> None:
        for i in range(self.num_downstream):
            self.output_queue.put(
                [
                    {
                        self.name: self.state,
                    }
                ]
            )

    def listen(self) -> None:
        dep_outputs: dict[str, list[dict[str, Any]]] = {}
        for dep in self.dependencies:
            dep_outputs[dep.name] = dep.output_queue.get()
        log.info(f"Running node {self.name}  with received {len(dep_outputs)} dependencies")
        self.run(dep_outputs)
