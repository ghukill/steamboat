import logging

from setter.core.step import Step, StepConnection
from setter.core.result import NoneResult, NumericResult
from setter.core.runner import Runner

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_dag_combine_and_split(combine_and_split_dag_runner):
    runner = combine_and_split_dag_runner
    D = runner.get_step_by_name("D")
    E = runner.get_step_by_name("E")
    results = runner.run()
    assert isinstance(results[D], NumericResult)
    assert isinstance(results[E], NoneResult)
    assert len(runner.get_results(results_format="list")) == 2


def test_quick_run(generate_text_step, reverse_text_step):
    assert (
        Runner.quick_run([generate_text_step, reverse_text_step]).data
        == generate_text_step.data[::-1]
    )


def test_parallel_run(combine_and_split_dag_runner):
    runner = combine_and_split_dag_runner
    D = runner.get_step_by_name("D")
    E = runner.get_step_by_name("E")
    results = runner.parallel_run()
    assert isinstance(results[D], NumericResult)
    assert isinstance(results[E], NoneResult)
    assert len(runner.get_results(results_format="list")) == 2
