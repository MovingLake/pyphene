import queue
from typing import Any, Callable
import logging

log = logging.getLogger("node")


class Node:
    def __init__(self, name) -> None:
        self.name: str = name
        self.output_queue: queue.Queue = queue.Queue()
        self.dependencies: list[Node] = []
        self.num_downstream: int = 0
        self.state: dict[str, Any] = {}
        self.fun: Callable = lambda inputs, state: None
        self.exception: Exception = None

    def run(self, dep_inputs: dict[str, list[dict[str, Any]]]) -> list[dict]:
        # Run the node.
        try:
            out = self.fun(dep_inputs, self.state)
        except Exception as e:
            self.exception = e
            out = None
        if out is None:
            out = []
        if not isinstance(out, list):
            out = [out]
        for i in range(self.num_downstream):
            self.output_queue.put(out)
        # Always put one more for the graph to collect at the end.
        self.output_queue.put(out)
        return out

    def listen(self) -> Any:
        dep_outputs: dict[str, list[dict[str, Any]]] = {}
        for dep in self.dependencies:
            dep_outputs[dep.name] = dep.output_queue.get()
        log.info(f"Running node {self.name}  with received {len(dep_outputs)} dependencies")
        return self.run(dep_outputs)
