from steamboat.core.exceptions import *
from steamboat.core.result import *
from steamboat.core.runner import *
from steamboat.core.step import *


class Good(Step[NoneResult, NumericResult]):
    def run(self, context: StepContext) -> NumericResult:
        return NumericResult(data=42)


class WantsBigNumbers(Step[NumericResult, NumericResult]):
    def run(self, context: StepContext) -> NumericResult:
        num = context.result.data
        if num < 1_000_000:
            raise StepRunSkip(f"input number {num} too small")
        else:
            return NumericResult(data=num + 100)


class NotGonnaGetIt(Step[NumericResult, NumericResult]):
    def run(self, context: StepContext) -> NumericResult:
        return NumericResult(data=context.result.data + 100)


g, w, n = Good(), WantsBigNumbers(), NotGonnaGetIt()
runner = Runner()
runner.add_connection(StepConnection(g, w))
runner.add_connection(StepConnection(w, n))
results = runner.run()

print(f"good result: {runner.get_connection(g,w)}")
print(f"step threw an exception: {runner.get_connection(w,n)}")
print(f"downstream step skipped because parent was skipped: {runner.get_connection(w,n)}")
