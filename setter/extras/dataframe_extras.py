"""setter.extras.dataframe_extras"""

import logging

from attr import attrs

from setter.core.result import LocalFileResult, StepResult

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dependencies_met = False
try:
    import pandas as pd

    dependencies_met = True
except ImportError:
    msg = "dependencies not met for 'dataframe_extras', install with setter[dataframe]"
    logger.warning(msg)

if dependencies_met:

    @attrs(auto_attribs=True)
    class DataFrameResult(StepResult):
        data: pd.DataFrame

    @attrs(auto_attribs=True)
    class CSVLocalFileResult(LocalFileResult):
        delimiter: str = ","

        def to_df(self) -> pd.DataFrame:
            # ruff: noqa: E501
            return pd.read_csv(self.filepath, delimiter=self.delimiter)  # type: ignore[arg-type]
