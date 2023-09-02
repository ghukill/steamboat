"""tests.test_step"""

from setter.core.result import StringResult
from setter.core.step import Step, StepContext, StepConnection


def test_generate_text_step(step_context_empty, generate_text_step):
    step = generate_text_step()
    assert step.run(step_context_empty) == StringResult(data="hello world!")
