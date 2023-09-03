import json
import logging
import os.path
from abc import abstractmethod
from collections.abc import Generator
from numbers import Number
from typing import TYPE_CHECKING, Optional, TypeVar

import pandas as pd
from attr import attrs

if TYPE_CHECKING:
    from setter.core.step import Step

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@attrs(auto_attribs=True)
class StepResult:
    data: None = None

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
class DataFrameResult(StepResult):
    data: pd.DataFrame
