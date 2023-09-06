from steamboat.core.result import NoneResult
from steamboat.core.step import Step, StepContext


class PrintHelloWorld(Step[NoneResult, NoneResult]):
    def run(self, context: StepContext) -> NoneResult:
        print("Hello World!")
        return NoneResult()


print("via Step.simulate()...")
PrintHelloWorld().simulate()
