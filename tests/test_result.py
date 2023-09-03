from setter.core.result import NoneResult, NumericResult, StringResult


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
