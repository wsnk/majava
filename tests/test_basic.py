import pytest
from majava import InInterval, IsInstance, DictContains, Absent, Round, Contains, Unordered
from majava.basic import StartsWith
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


def test_round():
    assert 3.14 == Round(3)
    assert 3.144 == Round(3.14, 2)
    with raises_assertion_error("Value 3.146 does not match: not ~3.14"):
        assert 3.146 == Round(3.14, 2)


def test_contains__list():
    m = Contains([1, 2, 3])

    assert repr(m) == "Contains([1, 2, 3])"
    assert [1, 2, 3, 4] == m
    assert [4, 3, 2, 1] == m
    with raises_assertion_error("Value [3, 4, 5] does not match: missing items: 1, 2"):
        assert [3, 4, 5] == m


def test_contains_ordered__list():
    m = Contains([2, 4], ordered=True)

    assert repr(m) == "ContainsOrdered([2, 4])"
    assert [1, 2, 3, 4] == m
    with raises_assertion_error("Value [4, 3, 2] does not match: 4 is not in order"):
        assert [4, 3, 2] == m


def test_contains__str():
    m = Contains(["ab", "cd"])

    assert repr(m) == "Contains(['ab', 'cd'])"
    assert "_ab_cd_" == m
    assert "cd__ab" == m
    with raises_assertion_error("Value '_ab_c_d_' does not match: missing items: 'cd'"):
        assert "_ab_c_d_" == m


def test_contains_ordered__str():
    m = Contains(["ab", "cd"], ordered=True)

    assert repr(m) == "ContainsOrdered(['ab', 'cd'])"
    assert "_ab cd_" == m
    with raises_assertion_error("Value '_cd ab_' does not match: 'cd' is not in order"):
        assert "_cd ab_" == m


def test_unordered__list():
    m = Unordered([1, 2, 3])

    assert repr(m) == "Unordered([1, 2, 3])"

    assert [1, 2, 3] == m
    assert [2, 3, 1] == m
    assert [3, 1, 2] == m

    with raises_assertion_error("Value [1, 2, 3, 4] does not match: len is not 3"):
        assert [1, 2, 3, 4] == m
    with raises_assertion_error("Value [1, 2, 4] does not match: missing items: 3"):
        assert [1, 2, 4] == m


def test_starts_with():
    m = StartsWith("no")

    assert repr(m) == "StartsWith('no')"

    assert "no money" == m
    assert "no niin" == m

    with raises_assertion_error("Value 'Honey' does not match: not StartsWith('no')"):
        assert "Honey" == m
