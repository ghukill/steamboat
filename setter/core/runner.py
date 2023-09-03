import logging
from collections import defaultdict, deque
from collections.abc import Generator
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Any, TypeVar, get_args, get_origin, Optional, Type

import networkx as nx
from IPython import embed
from networkx.classes.reportviews import EdgeView, NodeView

from setter.core.result import NoneResult, StepResult
from setter.core.step import Step, StepConnection, StepContext
from setter.utils.dagascii import draw as draw_graph

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class _RootStep(Step):
    def run(self, context: StepContext | None = None) -> NoneResult:
        return NoneResult()


class _TerminalStep(Step):
    def run(self, context: StepContext | None = None) -> NoneResult:
        return NoneResult()


class Runner:
    def __init__(self):
        self.dag = nx.DiGraph()
        self.root_step: _RootStep = _RootStep()
        self.terminal_step: _TerminalStep = _TerminalStep()
        self._results_dict: dict[Step, StepResult] | None = None

    def add_step(self, step: Step, step_attrs: dict | None = None) -> None:
        """Add a Step to the DAG."""
        step_attrs = step_attrs or {}
        step_attrs.setdefault("active", True)
        self.dag.add_node(step, **step_attrs)

    def get_step_by_name(self, name: str) -> Step:
        """Get Step instance by name

        QUESTION: should names be required unique across all Steps
        """
        for step in self.dag.nodes:
            if step.name == name:
                return step

    def add_connection(self, connection: StepConnection) -> None:
        """Add a Connection between two Steps."""
        for step in [connection.step, connection.caller]:
            if not self.dag.has_node(step):
                self.add_step(step)
        # self.dag.add_edge(connection.step, connection.next_step, **connection.args)
        self.dag.add_edge(
            connection.step, connection.caller, **{"connection": connection}
        )

    def clear(self) -> None:
        self.dag = nx.DiGraph()

    def topographic_step_sort(self) -> Generator[Step, Any, Any]:
        for step in nx.topological_sort(self.dag):
            yield step

    def parallel_topographic_step_sort(self):
        levels = []
        queue = deque()
        in_degree = {}

        for node in self.dag.nodes():
            in_degree[node] = self.dag.in_degree(node)
            # Nodes with in-degree 0 can be processed immediately
            if in_degree[node] == 0:
                queue.append(node)

        while queue:
            current_level = []
            for _ in range(len(queue)):
                node = queue.popleft()
                current_level.append(node)
                for neighbor in self.dag.neighbors(node):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)
            levels.append(current_level)

        return levels

    def graph_to_ascii(self) -> str:
        return draw_graph(list(self.dag.nodes), list(self.dag.edges))

    def log_as_ascii(self) -> None:
        if len(self.dag.nodes) == 0:
            return
        logger.info(f"\n{self.graph_to_ascii()}")
        logger.info(f"topographic sort: {list(self.topographic_step_sort())}")

    def finalize_dag(self) -> None:
        """
        Method to finalize the DAG before processing Steps
        """
        logger.info("finalizing DAG")
        old_root_steps = [
            node
            for node, in_degree in self.dag.in_degree
            if in_degree == 0 and not isinstance(node, _RootStep)
        ]
        for old_root_step in old_root_steps:
            self.add_connection(StepConnection(self.root_step, old_root_step))
        old_terminal_steps = [
            node
            for node, out_degree in self.dag.out_degree
            if out_degree == 0 and not isinstance(node, _TerminalStep)
        ]
        for old_terminal_step in old_terminal_steps:
            self.add_connection(StepConnection(old_terminal_step, self.terminal_step))

    def get_feeders(self, step: Step):
        for step in self.dag.predecessors(step):
            yield step

    def get_callers(self, step: Step):
        for step in self.dag.successors(step):
            yield step

    def get_connection(self, step, caller):
        return self.dag.edges[(step, caller)]["connection"]

    @property
    def terminal_feeder_steps(self):
        return list(self.get_feeders(self.terminal_step))

    @property
    def terminal_feeder_connections(self):
        return [
            self.get_connection(step, self.terminal_step)
            for step in self.terminal_feeder_steps
        ]

    def get_terminal_results(self) -> dict:
        return {
            connection.step: connection.result
            for connection in self.terminal_feeder_connections
        }

    def get_results(self, results_format: str):
        """Get results of all Steps that feed into TerminalStep.

        The results are saved on the Step --> TerminalStep StepConnection.
        """
        # parse and cache results
        if self._results_dict is None:
            self._results_dict = self.get_terminal_results()

        # prepare output
        results_format = results_format.lower().strip()
        if results_format == "dict":
            return self._results_dict
        elif results_format == "list":
            return [result for result in self._results_dict.values()]
        elif results_format == "scalar":
            results = [result for result in self._results_dict.values()]
            if len(results) != 1:
                raise Exception(
                    "0 or multiple results found, cannot return scalar StepResult"
                )
            return results[0]
        else:
            raise Exception(f"Unknown results format: {results_format}")

    def prepare_step_context(self, step, caller):
        logging.info(f"preparing step context: {step} --> {caller}")
        return StepContext(
            caller_connection=self.get_connection(step, caller),
            feeder_connections={
                feeder: self.get_connection(feeder, step)
                for feeder in self.get_feeders(step)
            },
        )

    def run_step(self, step):
        for caller in self.get_callers(step):
            context = self.prepare_step_context(step, caller)
            logger.info(f"running Step: {step} with context: {context}")
            result = step.run(context)
            context.caller_connection.result = result

    def run(
        self,
        results_format="dict",
        exclude_steps: list[Step] | None = None,
    ):
        """ """
        t0 = time.time()
        exclude_steps = exclude_steps or []

        self.finalize_dag()

        self.log_as_ascii()

        for step in self.topographic_step_sort():
            if step in exclude_steps:
                logger.warning(f"excluding step: {step}")
                continue
            self.run_step(step)

        logger.info(f"elapsed: {time.time() - t0}")
        return self.get_results(results_format)

    @classmethod
    def quick_run(cls, step_classes: list[Type[Step]]):
        """Quick run of simple, sequential steps, resulting in a single result."""
        runner = cls()
        steps = [step_class() for step_class in step_classes]
        adjacent_steps = list(zip(steps, steps[1:]))
        for step, caller in adjacent_steps:
            runner.add_connection(StepConnection(step, caller))
        return runner.run(results_format="scalar")

    def parallel_run(
        self,
        results_format="dict",
    ):
        """Run DAG Steps in parallel where possible."""
        t0 = time.time()
        self.finalize_dag()
        self.log_as_ascii()

        for layer in self.parallel_topographic_step_sort():
            logger.info(f"Running steps in parallel from layer: {layer}")

            with ThreadPoolExecutor() as executor:
                future_to_step = {
                    executor.submit(self.run_step, step): step for step in layer
                }
                for future in as_completed(future_to_step):
                    step = future_to_step[future]
                    try:
                        future.result()
                    except Exception as exc:
                        logger.error(f"{step} generated an exception: {exc}")

        logger.info(f"elapsed: {time.time()-t0}")
        return self.get_results(results_format)
