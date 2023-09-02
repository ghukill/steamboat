"""core.step"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from typing import Any, Generic, get_type_hints, Optional

from attr import attrs, attrib

from setter.core.result import Input_StepResult, NoneResult, Output_StepResult, StepResult

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Step(ABC, Generic[Output_StepResult]):
    """Unit of work in a Setter DAG."""

    # ruff: noqa: ARG002
    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        self.name = name or self.__class__.__name__
        self.result: StepResult | None = None
        self.caller_result: dict[Step, StepResult] | None = defaultdict(NoneResult)

    def __repr__(self) -> str:
        # ruff: noqa: D105
        return f"<Step: {self.name}>"

    def __str__(self) -> str:
        # ruff: noqa: D105
        return self.__repr__()

    @abstractmethod
    def run(self, context: "StepContext") -> Output_StepResult:
        """Primary run method for Step.

        :param context: StepContext instance, containing Runner information and upstream
            Steps
        """


class StepContext:
    """Context in which the Step is invoked."""

    # ruff: noqa: ARG002
    def __init__(
        self,
        caller_connection: Optional["StepConnection"] | None = None,
        feeder_connections: dict["StepConnection", "StepConnection"] | None = None,
    ) -> None:
        self.caller_connection = caller_connection or None
        self.feeder_connections = feeder_connections or {}

    def __repr__(self) -> str:
        # ruff: noqa: D105
        return f"<StepContext: caller={self.caller}, feeders={self.feeders}>"

    def __str__(self) -> str:
        # ruff: noqa: D105
        return self.__repr__()

    @property
    def step(self):
        return self.caller_connection.step

    @property
    def caller(self):
        return self.caller_connection.caller

    @property
    def feeders(self):
        return [feeder for feeder in self.feeder_connections.keys()]

    @property
    def results(self):
        """Return the results of this Context.

        A StepContext always has ONE caller Step, but may have MULTIPLE feeder Steps.
        For convenience, if only a single feeder Step is present, return that StepResult
        as a scalar value here.  Otherwise, return a list of StepResults.
        """
        feeder_results = [
            connection.result for connection in self.feeder_connections.values()
        ]
        if len(feeder_results) == 1:
            return feeder_results[0]
        return feeder_results


@attrs(auto_attribs=True)
class StepConnection:
    """Directional connection between Step and "caller" Step.

    Example: X --> Y

    When X.run() is invoked, it's always in the context of a "calling" Step, even if this
    Step is the TerminalStep.  We can say that X was "called" by Y.  This becomes
    relevant if Y may pass additional arguments for X to, optionally, consider during
    running.  For all these reasons, the result of X's output is stored on this
    StepConnection which is unique to "X being called by Y".
    """

    step: Step
    caller: Step
    args: dict = attrib(factory=dict)
    result: StepResult = attrib(factory=NoneResult)
