from lxml import etree

from setter.extras.xml_extras import XMLLocalFileResult, RepeatingXMLElementsGenerator
from setter.core.step import Step, StepConnection, StepContext
from setter.core.result import NoneResult
from setter.core.runner import Runner


class ProvideTestXMLFile(Step):
    def run(self, context: StepContext) -> XMLLocalFileResult:
        return XMLLocalFileResult(filepath="tests/fixtures/xml_no_ns.xml")


class Printer(Step):
    def run(self, context: StepContext) -> NoneResult:
        for i, record in enumerate(context.results.data):
            print(f"record: {i}")
            print(f"element: {etree.tostring(record).strip()}")
            print(f"text: {record.text}")
        return NoneResult()


runner = Runner()
er = RepeatingXMLElementsGenerator()  # NOTE: look into passing args via Step init
runner.add_connection(StepConnection(ProvideTestXMLFile(), er))
runner.add_connection(StepConnection(er, Printer(), args={"xpath": "//record"}))
result = runner.run(results_format="scalar")
