import pytest
from majava import DictContains, Any
from majava.formats import IsJson


@pytest.mark.parametrize("actual, expected", [
    ("[1, 2, 3]", IsJson()),
    ("[1, 2, 3]", IsJson([1, 2, 3])),
    ('{"a": 1, "b": 2}', IsJson({"a": 1, "b": 2})),
    (
        '{"a": 1, "b": 2}',
        IsJson(DictContains({"b": 2}))
    ),
    (
        '''{
            "a": "[1, 2, 3.14, 4]",
            "b": "any value may be here",
            "c": {"x": 1, "y": 2}
        }''',
        IsJson({
            "a": IsJson([1, 2, Any, 4]),
            "b": Any,
            "c": DictContains({"x": 1})
        })
    )
])
def test_is_json__match(actual, expected):
    assert actual == expected


@pytest.mark.parametrize("actual, expected, reason", [
    (None, {}, (
        "Value None at 'FromJSON' does not match: invalid type - "
        "the JSON object must be str, bytes or bytearray, not NoneType"
    )),
    ("", {}, (
        "Value '' at 'FromJSON' does not match: invalid JSON - "
        "Expecting value: line 1 column 1 (char 0)"
    )),
    (
        '''{
            "a": "[1, 2, 3.14, 4.14]",
            "b": "any value may be here",
            "c": {"x": 1, "y": 2}
        }''',
        {
            "a": IsJson([1, 2, Any, 4]),
            "b": Any,
            "c": DictContains({"x": 1})
        },
        (
            "Value [1, 2, 3.14, 4.14] at 'FromJSON.a.FromJSON' does not match: "
            "[1, 2, 3.14, 4.14] != [1, 2, <Any>, 4]'"
        )
    )
])
def test_is_json__mismatch(actual, expected, reason):
    with pytest.raises(AssertionError) as e:
        assert actual == IsJson(expected)

    err_message = str(e.value)
    reason = err_message.splitlines()[-1].strip()
    assert reason == reason
