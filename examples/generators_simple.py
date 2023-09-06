from steamboat.core.result import *
from steamboat.core.runner import *
from steamboat.core.step import *


class NumberGenerator(Step[NoneResult, GeneratorResult]):
    def run(self, context: StepContext) -> GeneratorResult:
        def func():
            for i in range(0, 10):
                print(f"[Step NumberGenerator] - producing number: {i}")
                yield i

        return GeneratorResult(data=func())


class FruitPickerInstructions(Step[NoneResult, GeneratorResult]):
    def run(self, context: StepContext) -> GeneratorResult:
        fruits = [
            "apple",
            "banana",
            "orange",
            "mango",
            "grape",
            "watermelon",
            "strawberry",
            "pineapple",
            "peach",
            "kiwi",
        ]

        def func():
            for i in context.results.data:
                fruit_pick_instruction = f"{i} {fruits[i]}s"
                print(
                    f"[Step FruitPickerInstructions] - fruit pick instruction: {fruit_pick_instruction}"
                )
                yield fruit_pick_instruction

        return GeneratorResult(data=func())


class FruitPicker(Step[GeneratorResult, NumericResult]):
    def run(self, context: StepContext) -> ListResult:
        instructions = []
        for instruction in context.results.data:
            print(f"[Step FruitPicker] - picking per instruction: {instruction}\n")
            instructions.append(instruction)
        return ListResult(data=instructions)


result = Runner.run_quick([NumberGenerator, FruitPickerInstructions, FruitPicker])
print("And the final list of instructions, each generated in their own sequential steps")
print(result.data)
