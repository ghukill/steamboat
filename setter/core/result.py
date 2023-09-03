"""core.result"""

import logging
from typing import Any, TypeVar

import pandas as pd
from attr import attrs

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@attrs(auto_attribs=True)
class StepResult:
    data: Any = None

    def __str__(self) -> str:
        # ruff: noqa: D105
        return f"<{self.__class__.__name__}>"


# generic types for input and output data
Input_StepResult = TypeVar("Input_StepResult", bound=StepResult)
Output_StepResult = TypeVar("Output_StepResult", bound=StepResult)


@attrs(auto_attribs=True)
class NoneResult(StepResult):
    """StepResult indicating nothing exists or was returned from Step."""

    data: None = None


@attrs(auto_attribs=True)
class StringResult(StepResult):
    data: str


@attrs(auto_attribs=True)
class NumericResult(StepResult):
    data: int | float


@attrs(auto_attribs=True)
class ListResult(StepResult):
    data: list | tuple


@attrs(auto_attribs=True)
class DictResult(StepResult):
    data: dict


@attrs(auto_attribs=True)
class DataFrameResult(StepResult):
    data: pd.DataFrame
