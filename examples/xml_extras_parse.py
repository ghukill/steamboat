import logging

from lxml import etree

from setter.extras.xml_extras import XMLLocalFileResult, RepeatingXMLElementsGenerator
from setter.core.step import Step, StepConnection, StepContext
from setter.core.result import NoneResult
from setter.core.runner import Runner

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ProvideTestXMLFile(Step):
    def run(self, context: StepContext) -> XMLLocalFileResult:
        return XMLLocalFileResult(filepath="tests/fixtures/xml_no_ns.xml")


class Printer(Step):
    def run(self, context: StepContext) -> NoneResult:
        logging.info("PRINTER OUTPUT #############################################")
        for i, record in enumerate(context.results.data):
            logging.info(f"record: {i}")
            logging.info(f"element: {etree.tostring(record).strip()}")
            logging.info(f"text: {record.text}")
        logging.info("############################################################")
        return NoneResult()


# Caller Step provides connection arguments with XPath
runner = Runner()
er = RepeatingXMLElementsGenerator()
runner.add_connection(StepConnection(ProvideTestXMLFile(), er))
runner.add_connection(StepConnection(er, Printer(), args={"xpath": "//record"}))
runner.run(results_format="scalar")

# RepeatingXMLElementsGenerator initiated with XPath
runner = Runner()
er = RepeatingXMLElementsGenerator(xpath="//record")
runner.add_connection(StepConnection(ProvideTestXMLFile(), er))
runner.add_connection(StepConnection(er, Printer()))
runner.run(results_format="scalar")
