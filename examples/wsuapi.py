"""
Make 10 parallel requests to an API endpoint and combine into a DataFrame
"""
import pandas as pd
import requests

from steamboat.core.result import NoneResult, StepResult
from steamboat.core.runner import Runner
from steamboat.core.step import Step, StepContext, StepConnection
from steamboat.extras.dataframe_extras import DataFrameResult


class WSUAPIResult(StepResult):
    data: requests.Response

    @property
    def records(self) -> list:
        return self.data.json()["response"]["solr_results"]["response"]["docs"]


class WSUAPIFetch(Step[NoneResult, WSUAPIResult]):
    def run(self, context: StepContext) -> WSUAPIResult:
        search_term = context.caller_args.get("search_term")
        url = f'https://digital.library.wayne.edu/api/search?q="{search_term}"'
        response = requests.get(url)
        if response.status_code == 200:
            return WSUAPIResult(data=response)


class RecordsToDataframe(Step):
    def run(self, context: "StepContext") -> DataFrameResult:
        dfs = []
        for connection in context.feeder_connections.values():
            df = pd.DataFrame(connection.result.records)
            df["search_term"] = connection.args["search_term"]
            dfs.append(df)
        return DataFrameResult(data=pd.concat(dfs))


runner = Runner()
records_to_df = RecordsToDataframe()
for search_term in [
    "horse",
    "snow",
    "palm tree",
    "detroit",
    "sketches and scraps",
    "packard",
    "michigan",
    "jacket",
    "dress",
    "airplane",
]:
    runner.add_connection(
        StepConnection(
            WSUAPIFetch(name=f"Search '{search_term}'"),
            records_to_df,
            args={"search_term": search_term},
        )
    )

df = runner.run_parallel(results_format="scalar").data
for idx, row in df.iterrows():
    print(row.search_term, "-->", row.dc_title[0])
