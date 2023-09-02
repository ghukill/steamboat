import logging

from setter.core.step import Step, StepConnection
from setter.core.result import NoneResult, NumericResult
from setter.core.runner import Runner

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_dag_combine_and_split():
    class Generate42(Step):
        def run(self, context) -> NumericResult:
            return NumericResult(data=42)

    class AddNumbers(Step):
        def run(self, context) -> NumericResult:
            logger.info("Adding numbers...")
            # TODO: improve the ergonomics of getting feeder results
            return NumericResult(
                data=sum(
                    [feeder.result.data for feeder in context.feeder_connections.values()]
                )
            )

    class EvaluateNumber(Step):
        def run(self, context) -> NumericResult | NoneResult:
            if context.caller_connection.args["checker"](context.results.data):
                return NumericResult(data=84)
            else:
                return NoneResult()

    class NumberPrinter(Step):
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

    results = runner.run()

    assert isinstance(results[d], NumericResult)
    assert isinstance(results[e], NoneResult)
    assert len(runner.get_results(results_format="list")) == 2
