import os.path

import pytest

from setter.core.result import (
    JSONLocalFileResult,
    LocalFileResult,
    NoneResult,
    NumericResult,
    StringResult,
)


def test_none_result():
    result = NoneResult()
    assert result.data is None


def test_string_result():
    data = "hello world!"
    result = StringResult(data=data)
    assert result.data == data


def test_numeric_result():
    data = 42
    result = NumericResult(data=42)
    assert result.data == data


def test_local_file_result():
    filepath = "tests/scratch/test.txt"
    if os.path.exists(filepath):
        os.remove(filepath)
    file_result = LocalFileResult(filepath=filepath, protected=False)
    assert file_result.filepath == filepath
    assert not file_result.file_exists
    with open(filepath, "w") as f:
        f.write("Hello World!")
    assert file_result.file_exists
    file_result.protected = True
    with pytest.raises(PermissionError):
        assert file_result.remove_file()
    file_result.protected = False
    assert file_result.remove_file()
    assert not file_result.file_exists
    assert not file_result.remove_file()


def test_json_local_file_result():
    filepath = "tests/fixtures/test.json"
    json_result = JSONLocalFileResult(filepath=filepath)
    assert json_result.filepath == filepath
    d = json_result.to_dict()
    assert len(d) == 3
    json_result.filepath = "tests/scratch/test_out.json"
    json_result.to_file()
    assert os.path.exists(json_result.filepath)


@pytest.mark.dataframe_extras()
def test_csv_local_file_result():
    from setter.extras.dataframe_extras import CSVLocalFileResult

    # CSV
    result = CSVLocalFileResult(filepath="tests/fixtures/test.csv", delimiter=",")
    df = result.to_df()
    assert len(df) == 3

    # TSV
    result = CSVLocalFileResult(filepath="tests/fixtures/test.tsv", delimiter="\t")
    df = result.to_df()
    assert len(df) == 3


@pytest.mark.xml_extras()
def test_xml_local_file_namespace_parser():
    from setter.extras.xml_extras import XMLLocalFileResult

    r1 = XMLLocalFileResult(filepath="tests/fixtures/xml_no_ns.xml")
    assert r1.get_nsmap() == {}

    r2 = XMLLocalFileResult(filepath="tests/fixtures/xml_root_ns.xml")
    assert r2.get_nsmap() == {"ns": "http://example.com/ns"}

    r3 = XMLLocalFileResult(filepath="tests/fixtures/xml_element_ns.xml")
    assert r3.get_nsmap() == {"ns0": "http://example.com/ns"}
