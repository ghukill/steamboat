"""steamboat.extras.xml_extras"""

import logging
from collections.abc import Generator

from attr import attrs

from steamboat.core.result import GeneratorResult, LocalFileResult, StepResult
from steamboat.core.step import Step, StepContext

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dependencies_met = False
try:
    from lxml import etree  # type: ignore[import]

    dependencies_met = True
except ImportError:
    msg = "dependencies not met for 'xml_extras', install with steamboat[xml]"
    logger.warning(msg)

if dependencies_met:

    @attrs(auto_attribs=True)
    class XMLResult(StepResult):
        data: str | bytes | None
        _tree: etree._ElementTree | None = None

        def get_tree(self) -> etree._ElementTree:
            if self._tree is None:
                self._tree = etree.fromstring(self.data).getroottree()
            return self._tree

        def get_root(self) -> etree._Element:
            tree = self.get_tree()
            return tree.getroot()

        def get_nsmap(self, namespace_mixins: dict[str, str] | None = None) -> dict:
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

            if namespace_mixins is not None:
                nsmap.update(namespace_mixins)

            return nsmap

    @attrs(auto_attribs=True)
    class XMLLocalFileResult(LocalFileResult, XMLResult):
        def get_tree(self) -> etree._ElementTree:
            if self._tree is None:
                self._tree = etree.parse(self.filepath)
            return self._tree

    class RepeatingXMLElementsGenerator(Step[XMLLocalFileResult, GeneratorResult]):
        """Step to return a Generator of a repeating element."""

        def __init__(
            self,
            xpath: str | None = None,
            lxml_findall: str | None = None,
            namespace_mixins: dict[str, str] | None = None,
        ):
            super().__init__()
            self.xpath = xpath
            self.lxml_findall = lxml_findall
            self.namespace_mixins = namespace_mixins

        def run(self, context: StepContext[XMLLocalFileResult]) -> GeneratorResult:
            xpath = context.caller_args.get("xpath") or self.xpath
            lxml_findall = context.caller_args.get("lxml_findall") or self.lxml_findall

            def yield_elements_func() -> Generator[etree._Element, None, None]:
                xml_file_result = context.result

                tree = xml_file_result.get_tree()

                # XPath
                xpath_elements = []  # type: ignore[var-annotated]
                if xpath is not None:
                    nsmap = xml_file_result.get_nsmap(
                        namespace_mixins=self.namespace_mixins
                    )
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
                    # yield element
                    yield XMLResult(data=etree.tostring(element))

            return GeneratorResult(data=yield_elements_func())
