"""tests.conftest"""

import logging

import pytest

from setter.core.result import NoneResult, NumericResult, StringResult
from setter.core.runner import Runner
from setter.core.step import Step, StepConnection, StepContext

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@pytest.fixture
def step_context_empty():
    return StepContext()


@pytest.fixture
def generate_text_step():
    class GenerateText(Step[NoneResult, StringResult]):
        data = "hello world!"

        def run(self, context: StepContext) -> StringResult:
            return StringResult(data=self.data)

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


@pytest.fixture
def combine_and_split_dag_runner():
    class Generate42(Step[NoneResult, NumericResult]):
        def run(self, context) -> NumericResult:
            return NumericResult(data=42)

    class AddNumbers(Step[NumericResult, NumericResult]):
        def run(self, context) -> NumericResult:
            logger.info("Adding numbers...")
            return NumericResult(data=sum([result.data for result in context.results]))

    class EvaluateNumber(Step[NumericResult, NumericResult | NoneResult]):
        def run(self, context) -> NumericResult | NoneResult:
            if context.caller_connection.args["checker"](context.results.data):
                return NumericResult(data=84)
            else:
                return NoneResult()

    class NumberPrinter(Step[NumericResult | NoneResult, NoneResult]):
        def run(self, context) -> NoneResult | NoneResult:
            res = context.results
            if isinstance(res, NumericResult):
                logging.info(f"We got a number! {res.data}")
            else:
                logging.info("Nothing for us...")
            return res

    a = Generate42(name="A")
    b = Generate42(name="B")
    c = AddNumbers(name="C")
    x = EvaluateNumber(name="X")
    d = NumberPrinter(name="D")
    e = NumberPrinter(name="E")

    runner = Runner()

    runner.add_connection(StepConnection(a, c))
    runner.add_connection(StepConnection(b, c))
    runner.add_connection(StepConnection(c, x))
    runner.add_connection(StepConnection(x, d, {"checker": lambda x: x < 100}))
    runner.add_connection(StepConnection(x, e, {"checker": lambda x: x >= 100}))

    return runner
