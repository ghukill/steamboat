from setter.core.result import NoneResult
from setter.core.step import Step, StepContext


class PrintHelloWorld(Step[NoneResult, NoneResult]):
    def run(self, context: StepContext) -> NoneResult:
        print("Hello World!")
        return NoneResult()


print("via Step.simulate()...")
PrintHelloWorld().simulate()
print("via Step.run()...")
PrintHelloWorld().run(StepContext())
