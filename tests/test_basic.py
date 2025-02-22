from majava import InInterval, IsInstance, Round, StartsWith, EndsWith, LengthIs, HasAttrs, \
    Any, Absent
from .common import raises_assertion_error


def test_is_instance():
    m = IsInstance(int, str)

    assert str(m) == "IsInstance(int|str)"
    assert 1 == m
    assert "2" == m
    with raises_assertion_error("Value 1.1 does not match: not IsInstance(int|str)"):
        assert 1.1 == m


def test_round():
    assert repr(Round(3.14)) == "Round(3.0)"
    assert repr(Round(3.14, 2)) == "Round(3.14)"

    assert 3.0 == Round(3.14)
    assert 3.14 == Round(3.14)
    assert 3.144 == Round(3.14, 2)

    with raises_assertion_error("Value 3.146 does not match: not ~3.14"):
        assert 3.146 == Round(3.14, 2)


def test_starts_with():
    m = StartsWith("no")

    assert repr(m) == "StartsWith('no')"
    assert "no money" == m
    assert "no niin" == m
    with raises_assertion_error("Value 'Honey' does not match: not StartsWith('no')"):
        assert "Honey" == m


def test_ends_with():
    m = EndsWith("yes")

    assert repr(m) == "EndsWith('yes')"
    assert "yes" == m
    assert "told yes" == m
    with raises_assertion_error("Value 'yes my lord' does not match: not EndsWith('yes')"):
        assert "yes my lord" == m


def test_in_interval():
    m = InInterval(1, 7)

    assert repr(m) == "InInterval(1, 7)"
    assert 1 == m
    assert 4 == m
    assert 7 == m
    with raises_assertion_error("Value 10 does not match: not InInterval(1, 7)"):
        assert 10 == m


def test_length_is():
    m = LengthIs(3)

    assert repr(m) == "LengthIs(3)"
    assert [1, 2, 3] == m
    assert "abc" == m
    with raises_assertion_error("Value 'abcd' does not match: not LengthIs(3)"):
        assert "abcd" == m


def test_has_attrs():
    class AttrDict(dict):
        def __getattr__(self, key):
            if key not in self:
                raise AttributeError(key)
            return self[key]

    m = HasAttrs(a=1, b=Any, c=Absent)

    assert repr(m) == "HasAttrs(a=1, b=<Any>, c=<Absent>)"
    assert AttrDict({"a": 1, "b": 2}) == m
    assert AttrDict({"a": 1, "b": None, "x": 3}) == m

    with raises_assertion_error("Value 2 at 'a' does not match: 2 != 1"):
        assert AttrDict({"a": 2, "b": 2}) == m
    with raises_assertion_error("Value <Absent> at 'b' does not match: missing item"):
        assert AttrDict({"a": 1}) == m
    with raises_assertion_error("Value 3 at 'c' does not match: unexpected item"):
        assert AttrDict({"a": 1, "b": 2, "c": 3}) == m
