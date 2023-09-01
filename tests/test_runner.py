from setter.core.step import Step, StepConnection
from setter.core.result import NoneResult, NumericResult
from setter.core.runner import Runner


def test_runner_combine_and_split():
    class Generate42(Step):
        def run(self, context) -> NumericResult:
            return NumericResult(data=42)

    class AddNumbers(Step):
        def run(self, context) -> NumericResult:
            return NumericResult(data=sum([result.data for result in context.results]))

    class EvaluateNumber(Step):
        def run(self, context) -> NumericResult | NoneResult:
            if context.caller_args["checker"](context.results.data):
                return NumericResult(data=84)
            else:
                return NoneResult()

    class NumberPrinter(Step):
        def run(self, context) -> NoneResult:
            res = context.results
            if isinstance(res, NumericResult):
                print(f"We got a number! {res.data}")
            else:
                print("Nothing for us...")
            return NoneResult()

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
