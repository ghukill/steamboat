import logging
import time

from steamboat.core.result import NoneResult, NumericResult
from steamboat.core.runner import Runner
from steamboat.core.step import Step, StepConnection, StepContext

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
        Runner.run_quick([generate_text_step, reverse_text_step]).data
        == generate_text_step.data[::-1]
    )


def test_parallel_run(combine_and_split_dag_runner):
    runner = combine_and_split_dag_runner
    D = runner.get_step_by_name("D")
    E = runner.get_step_by_name("E")
    results = runner.run_parallel()
    assert isinstance(results[D], NumericResult)
    assert isinstance(results[E], NoneResult)
    assert len(runner.get_results(results_format="list")) == 2


def test_parallel_faster_than_sequential_when_waiting():
    class Sleeper(Step):
        def run(self, context: StepContext) -> NumericResult:
            t0 = time.time()
            time.sleep(1)
            elapsed = time.time() - t0
            return NumericResult(data=elapsed)

    class Combiner(Step[NumericResult, NumericResult]):
        def run(self, context: "StepContext") -> NumericResult:
            return NumericResult(data=sum([result.data for result in context.results]))

    # sequential
    t0 = time.time()
    s1 = Sleeper(name="s1")
    s2 = Sleeper(name="s2")
    s3 = Sleeper(name="s3")
    c = Combiner(name="c")
    runner = Runner()
    runner.add_connection(StepConnection(s1, c))
    runner.add_connection(StepConnection(s2, c))
    runner.add_connection(StepConnection(s3, c))
    result = runner.run(results_format="scalar")
    elapsed = time.time() - t0
    assert elapsed > result.data  # assert that total time is MORE than sum of sleepers

    # parallel
    t0 = time.time()
    s1 = Sleeper(name="s1")
    s2 = Sleeper(name="s2")
    s3 = Sleeper(name="s3")
    c = Combiner(name="c")
    runner = Runner()
    runner.add_connection(StepConnection(s1, c))
    runner.add_connection(StepConnection(s2, c))
    runner.add_connection(StepConnection(s3, c))
    result = runner.run_parallel(results_format="scalar")
    elapsed = time.time() - t0
    assert elapsed < result.data  # assert that total time is LESS than sum of sleepers
