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
        feeders: list[Step] | None = None,
        connection: Optional["StepConnection"] | None = None,
    ) -> None:
        self.feeders = feeders or []
        self.connection = connection or None

    def __repr__(self) -> str:
        # ruff: noqa: D105
        return f"<StepContext: feeders={self.feeders}, caller={self.caller}>"

    def __str__(self) -> str:
        # ruff: noqa: D105
        return self.__repr__()

    @property
    def step(self):
        return self.connection.step

    @property
    def caller(self):
        return self.connection.caller

    @property
    def results(self):
        feeder_results = [feeder.caller_result[self.step] for feeder in self.feeders]
        # QUESTION: return scalar if list 1?
        if len(feeder_results) == 1:
            return feeder_results[0]
        return feeder_results


@attrs(auto_attribs=True)
class StepConnection:
    """Directional connection between two Steps.

    Example: X --> Y
    The result of this connection where Y is "calling" X, is stored on this Connection
    by the Runner.  The Step X merely returns a value, but the Runner is aware of which
    "caller" invoked it.
    """

    step: Step
    caller: Step
    args: dict = attrib(factory=dict)
