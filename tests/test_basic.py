import pytest
from majava import InInterval, IsInstance, DictContains, Absent
from .common import raises_assertion_error


def test_in_interval():
    interval = InInterval(1, 7)

    assert 1 == interval
    assert 4 == interval
    assert 7 == interval

    with raises_assertion_error("Value 10 does not match: not InInterval(1, 7)"):
        assert 10 == interval


def test_is_instance():
    int_or_str = IsInstance(int, str)

    assert str(int_or_str) == "IsInstance(int|str)"

    assert 1 == int_or_str
    assert "2" == int_or_str

    with raises_assertion_error("Value 1.1 does not match: not IsInstance(int|str)"):
        assert 1.1 == int_or_str


def test_dict_contains__plain():
    assert {"a": 1, "b": 2} == DictContains({"a": 1, "b": 2})
    assert {"a": 1, "b": 2} == DictContains({"a": 1})
    assert {"a": 1, "b": 2} == DictContains({"b": 2})
    assert {"a": 1, "b": 2} == DictContains({})


def test_dict_contains__absent():
    m = DictContains({"a": 1, "b": Absent})

    assert {"a": 1} == m
    with raises_assertion_error(
        "Value {'a': 1, 'b': 2, 'c': 3} does not match: unexpected items with keys: 'b'"
    ):
        assert {"a": 1, "b": 2, "c": 3} == m


@pytest.mark.parametrize("actual, expected, message", [
    ({"a": 1, "b": 2}, {"a": 1, "b": 3}, "Value 2 at 'b' does not match: 2 != 3"),
    ({"a": 1}, {"b": 1}, "Value {'a': 1} does not match: missing items with keys: 'b'")
])
def test_dict_contains__mismatch(actual, expected, message):
    with raises_assertion_error(message):
        assert actual == DictContains(expected)


@pytest.mark.parametrize("actual, expected, message", [
    (
        {"a": 1, "b": {"c": {"d": 2, "e": 3}}},
        {"b": {"c": {"e": 4}}},
        "Value 3 at 'b.c.e' does not match: 3 != 4"
    ),
])
def test_dict__nested_mismatch(actual, expected, message):
    with raises_assertion_error(message):
        assert actual == DictContains(expected)
