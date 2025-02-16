import pytest
from majava.matchers import matcher, MayBe, Or, Absent, Any
from .common import raises_assertion_error


def test_dict():
    assert {"a": 1, "b": 2} == matcher({"a": 1, "b": 2})
    assert {"a": 1, "b": 2} == matcher({"a": 1, "b": Any})
    assert {"a": 1} == matcher({"a": 1, "b": Absent})


def test_or():
    assert 1 == Or(1, 2)
    assert 2 == Or(1, 2)
    with raises_assertion_error("Value 4 does not match: is not 1 nor '2' nor MayBe({})"):
        assert 4 == Or(1, "2", MayBe({}))


def test_dict_with_submatchers():
    assert {"a": 1, "b": 2} == matcher({"a": 1, "b": Or(2, 3)})
    assert {"a": 1, "b": 3} == matcher({"a": 1, "b": Or(2, 3)})

    assert {"a": 1} == matcher({"a": 1, "b": MayBe(2)})
    assert {"a": 1, "b": 2} == matcher({"a": 1, "b": MayBe(2)})


@pytest.mark.parametrize("value, expectation, reason", [
    ({"a": 1}, {"a": 2}, "Value 1 at 'a' does not match: 1 != 2"),
    # unexpected items
    ({"a": 1}, {}, "Value {'a': 1} does not match: unexpected items with keys: 'a'"),
    (
        {"a": 1, "b": 2}, {},
        "Value {'a': 1, 'b': 2} does not match: unexpected items with keys: 'a', 'b'"
    ),
    # missing items
    ({}, {"a": 1}, "Value {} does not match: missing items with keys: 'a'"),
    ({}, {"a": 1, "b": 1}, "Value {} does not match: missing items with keys: 'a', 'b'"),
    # submatchers
    ({"a": 1}, {"a": MayBe(2)}, "Value 1 at 'a' does not match: 1 != 2"),
    ({"a": 1}, {"a": Or(2, 3, 4)}, "Value 1 at 'a' does not match: is not 2 nor 3 nor 4"),
])
def test_dict_mismatch(value, expectation, reason):
    with raises_assertion_error(reason):
        assert value == matcher(expectation)
