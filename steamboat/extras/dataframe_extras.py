"""steamboat.extras.dataframe_extras"""
# ruff: noqa: S608

import logging

from attr import attrs

from steamboat.core.result import LocalFileResult, StepResult

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dependencies_met = False
try:
    import duckdb
    import pandas as pd

    dependencies_met = True
except ImportError:
    msg = "dependencies not met for 'dataframe_extras', install with steamboat[dataframe]"
    logger.warning(msg)

if dependencies_met:

    @attrs(auto_attribs=True)
    class DataFrameResult(StepResult):
        data: pd.DataFrame

        def to_duckdb(self, table_name: str, filepath: str) -> bool:
            """
            Write Pandas dataframe to DuckDB persisted on disk
            """
            # create connection
            conn = duckdb.connect(database=filepath, read_only=False)

            # drop table if exists
            conn.sql(f"DROP TABLE IF EXISTS main.{table_name};")

            # register dataframe as view and persist to table
            conn.register(table_name, self.data)
            # ruff: noqa: S608
            conn.sql(f"CREATE TABLE main.{table_name} AS SELECT * FROM {table_name};")

            # commit and close
            conn.commit()
            conn.close()
            return True

    @attrs(auto_attribs=True)
    class DuckDbTableResult(LocalFileResult):
        """
        TODO: implement context manager for connection handling
        """

        table_name: str | None = None
        read_only: bool = False

        def get_connection(
            self, read_only: bool | None = None
        ) -> duckdb.DuckDBPyConnection:
            if read_only is None:
                read_only = self.read_only
            # ruff: noqa: E501
            return duckdb.connect(
                self.filepath, read_only=read_only  # type: ignore[arg-type]
            )  # type: ignore[arg-type]

        def to_df(self) -> pd.DataFrame:
            """
            Read DuckDB table into memory as Pandas dataframe
            """
            con = self.get_connection(read_only=True)
            df = con.execute(f"SELECT * FROM {self.table_name}").df()
            con.close()
            return df

    @attrs(auto_attribs=True)
    class CSVLocalFileResult(LocalFileResult):
        delimiter: str = ","

        def to_df(self) -> pd.DataFrame:
            # ruff: noqa: E501
            return pd.read_csv(self.filepath, delimiter=self.delimiter)  # type: ignore[arg-type]
