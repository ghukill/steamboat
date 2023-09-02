"""tests.conftest"""

import pytest

from setter.core.step import Step, StepContext, StepConnection
from setter.core.result import NoneResult, NumericResult, StringResult
from setter.core.runner import Runner


@pytest.fixture
def step_context_empty():
    return StepContext()


@pytest.fixture
def generate_text_step():
    class GenerateText(Step[NoneResult, StringResult]):
        def run(self, context: StepContext) -> StringResult:
            return StringResult(data="hello world!")

    return GenerateText


@pytest.fixture
def reverse_text_step():
    class ReverseText(Step[StringResult, StringResult]):
        def run(self, context: StepContext) -> StringResult:
            return StringResult(data=context.results.data[::-1])

    return ReverseText


@pytest.fixture
def generate_number_step():
    class GenerateNumber(Step[NoneResult, NumericResult]):
        def run(self, context: StepContext) -> NumericResult:
            return NumericResult(data=42)

    return GenerateNumber


@pytest.fixture
def generate_text_and_reverse_runner(generate_text_step, reverse_text_step):
    gt = generate_text_step()
    rt = reverse_text_step()
    runner = Runner()
    runner.add_connection(StepConnection(gt, rt))
    return runner
