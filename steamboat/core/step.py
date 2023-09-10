"""core.step"""

import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Generic, Optional, get_args, get_origin, get_type_hints

from attr import attrib, attrs

from steamboat.core.result import (
    Input_StepResult,
    NoneResult,
    Output_StepResult,
    StepResult,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Step(ABC, Generic[Input_StepResult, Output_StepResult]):
    """Unit of work in a Steamboat DAG."""

    # ruff: noqa: ARG002
    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        self._name = name or self.__class__.__name__

    @property
    def name(self):
        name = getattr(self, "_name", None) or self.__class__.__name__
        return name

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

    @property
    def return_type(self) -> type:
        """
        Property to inspect the returned type from the primary run method.
        """
        return get_type_hints(self.run)["return"]

    @property
    def expected_input_type(self) -> type | None:
        """Method to fetch the expected input type of a class extending Step.

        This works by using .__orig_bases__ which has the typed Generics that were used
        in this Step type's definition.

        Example:
        Goober(Step[StringResult, NumericResult])

        In this example, the Step type Goober is expecting a StringResult as input, and
        will return a NumericResult.  These are hydrating the Generic types for Step that
        are established in Step definition, Generic[Input_StepResult, Output_StepResult].
        """
        orig_bases = type(self).__orig_bases__  # type: ignore[attr-defined]
        for base in orig_bases:
            if get_origin(base) is Step:
                generic_args = get_args(base)
                expected_input_type = generic_args[0]
                # ruff: noqa: RET504
                return expected_input_type
        return None

    def _prepare_step_simulation_context(self, caller_args: dict) -> "StepContext":
        from steamboat.core.runner import _RootStep, _TerminalStep

        root_step, terminal_step = _RootStep(), _TerminalStep()
        context = StepContext(
            caller_connection=StepConnection(
                step=self, caller=terminal_step, args=caller_args
            ),
            feeder_connections={root_step: StepConnection(step=root_step, caller=self)},
        )
        return context

    def simulate(
        self, context: Optional["StepContext"] = None, caller_args: dict | None = None
    ) -> Output_StepResult:
        """Run a Step's .run method, providing a StepContext"""
        if context is None:
            caller_args = caller_args or {}
            context = self._prepare_step_simulation_context(caller_args)

        return self.run(context)


class StepContext:
    """Context in which the Step is invoked."""

    # ruff: noqa: ARG002
    def __init__(
        self,
        caller_connection: Optional["StepConnection"] = None,
        feeder_connections: dict[Step, "StepConnection"] | None = None,
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
    def step(self) -> Step | None:
        if self.caller_connection is not None:
            return self.caller_connection.step
        return None

    @property
    def caller(self) -> Step | None:
        if self.caller_connection is not None:
            return self.caller_connection.caller
        return None

    @property
    def caller_args(self) -> dict:
        if self.caller_connection is not None:
            return self.caller_connection.args
        return {}

    @property
    def feeders(self) -> list[Step]:
        return list(self.feeder_connections.keys())

    @property
    def results(self) -> StepResult | list[StepResult]:
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

    def validate(self) -> bool:
        """Validate a StepConnection

        Ensure the Step returns a value the caller Step is prepared to handle.
        """
        return self.step.return_type == self.caller.expected_input_type
