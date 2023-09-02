"""tests.test_step"""

from setter.core.result import StringResult
from setter.core.step import Step, StepContext, StepConnection


def test_generate_text_step(step_context_empty, generate_text_step):
    step = generate_text_step()
    assert step.run(step_context_empty) == StringResult(data="hello world!")


def test_validate_connection_success(generate_text_step, reverse_text_step):
    gt = generate_text_step()
    rt = reverse_text_step()
    connection = StepConnection(gt, rt)
    assert connection.validate()


def test_validate_connection_fail(generate_number_step, reverse_text_step):
    gt = generate_number_step()
    rt = reverse_text_step()
    connection = StepConnection(gt, rt)
    assert not connection.validate()
