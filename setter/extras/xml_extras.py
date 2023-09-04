"""setter.extras.xml_extras"""

import logging
from collections.abc import Generator

from attr import attrs

from setter.core.result import GeneratorResult, LocalFileResult
from setter.core.step import Step, StepContext

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dependencies_met = False
try:
    from lxml import etree  # type: ignore[import]

    dependencies_met = True
except ImportError:
    msg = "dependencies not met for 'xml_extras', install with setter[dataframe]"
    logger.warning(msg)

if dependencies_met:

    @attrs(auto_attribs=True)
    class XMLLocalFileResult(LocalFileResult):
        _tree: etree._ElementTree | None = None

        def read_file(self, read_mode: str = "rb") -> bytes | str:
            with open(self.filepath, read_mode) as f:
                return f.read()

        def get_tree(self) -> etree._ElementTree:
            if self._tree is None:
                self._tree = etree.parse(self.filepath)
            return self._tree

        def get_root(self) -> etree._Element:
            tree = self.get_tree()
            return tree.getroot()

        def get_nsmap(self) -> dict:
            def gather_all_namespaces(
                element: etree._Element, anon_count: int = 0
            ) -> dict:
                namespaces = {}
                namespaces.update(element.nsmap)
                for child in element:
                    element_level_ns = gather_all_namespaces(child, anon_count=anon_count)
                    new_element_level_ns = {}
                    for k, v in element_level_ns.items():
                        if k is None and v not in namespaces.values():
                            prefix = f"ns{anon_count}"
                            anon_count += 1
                            # ruff: noqa: PLW2901
                            k = prefix
                        new_element_level_ns[k] = v
                    namespaces.update(new_element_level_ns)
                return namespaces

            root = self.get_root()
            nsmap = gather_all_namespaces(root)
            if None in nsmap:
                nsmap.pop(None)

            return nsmap

    class RepeatingXMLElementsGenerator(Step[XMLLocalFileResult, GeneratorResult]):
        def run(self, context: StepContext) -> GeneratorResult:
            xpath = context.caller_args.get("xpath")
            lxml_findall = context.caller_args.get("lxml_findall")

            def yield_elements_func() -> Generator[etree._Element, None, None]:
                # NOTE: lack of typing because typed at list[StepResult]
                # ruff: noqa: E501
                xml_file_result: XMLLocalFileResult = context.results  # type: ignore [assignment]

                tree = xml_file_result.get_tree()

                # XPath
                xpath_elements = []  # type: ignore[var-annotated]
                if xpath is not None:
                    nsmap = xml_file_result.get_nsmap()
                    xpath_elements = tree.xpath(  # type: ignore[assignment]
                        xpath,
                        namespaces=nsmap,
                    )

                # lxml findall
                findall_elements = []  # type: ignore[var-annotated]
                if lxml_findall is not None:
                    findall_elements = tree.findall(lxml_findall)

                # dedupe elements if both approaches
                result = []
                seen = set()
                for element_list in [xpath_elements, findall_elements]:
                    for element in element_list:
                        if id(element) not in seen:
                            result.append(element)
                            seen.add(id(element))

                # yield to return a generator
                for element in result:
                    yield element

            return GeneratorResult(data=yield_elements_func())
