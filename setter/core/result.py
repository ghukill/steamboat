"""core.result"""
import json
import logging
import os
from abc import abstractmethod
from collections.abc import Generator
from os import PathLike
from typing import Any, TypeVar

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
class GeneratorResult(StepResult):
    data: Generator


@attrs(auto_attribs=True)
class DictResult(StepResult):
    data: dict


@attrs(auto_attribs=True)
class FileResult(StepResult):
    @property
    @abstractmethod
    def file_exists(self) -> bool:
        ...  # pragma: no cover

    @abstractmethod
    def read_file(self) -> bytes | str:
        ...  # pragma: no cover


@attrs(auto_attribs=True)
class LocalFileResult(FileResult):
    filepath: str | bytes | PathLike[str] | PathLike[bytes] = ""
    protected: bool = True

    @property
    def file_exists(self) -> bool:
        return os.path.exists(self.filepath)

    def remove_file(self) -> bool:
        if self.protected:
            raise PermissionError(
                f"File {self.filepath!r} has protected flag and may not be removed."
            )
        if self.file_exists:
            os.remove(self.filepath)
            return True
        return False

    def read_file(self, read_mode: str = "rb") -> bytes | str:
        with open(self.filepath, read_mode) as f:
            return f.read()


@attrs(auto_attribs=True)
class JSONLocalFileResult(LocalFileResult):
    data: dict | None = None

    def to_dict(self) -> dict:
        """
        Load JSON file as python dictionary
        """
        return json.loads(self.read_file())

    def to_file(self) -> bool:
        with open(self.filepath, "w") as f:
            f.write(json.dumps(self.data))
        return True
