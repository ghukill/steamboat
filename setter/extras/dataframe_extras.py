"""setter.extras.dataframe_extras"""

import pandas as pd
from attr import attrs

from setter.core.result import StepResult


@attrs(auto_attribs=True)
class DataFrameResult(StepResult):
    data: pd.DataFrame
