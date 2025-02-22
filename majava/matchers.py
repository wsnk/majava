from typing import Optional, Type, Callable
import inspect


class Mismatch(Exception):
    @classmethod
    def invalid_type(cls, value, expected_type, path=""):
        return cls(value, path, f"invalid type - got {type(value)}, expected {expected_type}")

    @classmethod
    def invalid_len(cls, value, expected_len, path=""):
        return cls(value, path, f"invalid length - got {len(value)}, expected {expected_len}")

    @classmethod
    def missing_keys(cls, value, keys, path=""):
        keys_str = ", ".join(repr(i) for i in keys)
        return cls(value, path, f"missing items with keys: {keys_str}")

    @classmethod
    def unexpected_keys(cls, value, keys, path=""):
        keys_str = ", ".join(repr(i) for i in keys)
        raise Mismatch(value, "", f"unexpected items with keys: {keys_str}")

    @classmethod
    def missing_items(cls, value, items, path=""):
        items_str = ", ".join(repr(i) for i in items)
        raise Mismatch(value, "", f"missing items: {items_str}")

    @classmethod
    def missing_item(cls, value, path=""):
        return cls(value, path, "missing item")

    @classmethod
    def unexpected_item(cls, value, path=""):
        return cls(value, path, "unexpected item")

    def __init__(self, value, path, msg):
        self.value = value
        self.path = path
        self.msg = msg

    def prepend(self, path):
        self.path = f"{path}.{self.path}" if self.path else path
        return self

    def __str__(self):
        if not self.path:
            return f"Value {repr(self.value)} does not match: {self.msg}"
        return f"Value {repr(self.value)} at {repr(self.path)} does not match: {self.msg}"


class Matcher:
    """ Base class for all matchers.
    """

    _mismatch = None

    def __eq__(self, other):
        try:
            self._match(other)
            self._mismatch = None
            return True
        except Mismatch as e:
            self._mismatch = e
            return False

    def __and__(self, other):
        return And(self, other)

    def __or__(self, other):
        return Or(self, other)

    def _match(self, other) -> Optional[str]:
        pass


def make_matcher(fn: Callable) -> Type[Matcher]:
    """ Decorates a function to become a matcher.
    """

    name = fn.__name__

    argspec = inspect.getfullargspec(fn)
    arg_count = len(argspec.args) - 1

    class M(Matcher):
        def __init__(self, *args, **kwargs):
            if len(args) != arg_count:
                raise TypeError(
                    f"{name}() takes {arg_count} positional arguments, {len(args)} were given")
            if argspec.varkw is None and kwargs:
                raise TypeError(
                    f"{name}() got an unexpected keyword argument '{next(iter(kwargs))}'")
            self.args = args
            self.kwargs = kwargs

        def __repr__(self):
            args_str = ", ".join(repr(i) for i in self.args)
            kwargs_str = ", ".join(f"{k}={v!r}" for k, v in self.kwargs.items())
            content_str = ", ".join(filter(None, [args_str, kwargs_str]))
            return f"{name}({content_str})"

        def _match(self, other):
            if fn(other, *self.args, **self.kwargs) is False:
                raise Mismatch(other, "", f"not {self}")

    M.__qualname__ = name
    M.__name__ = name
    M.__doc__ = fn.__doc__

    return M


class _MatcherWrap(Matcher):
    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return repr(self.v)

    def _match(self, other):
        _match(self.v, other)


def matcher(value) -> Matcher:
    """ Makes a matcher from the given value.
    It allows to get similar message on AssertionError in pytest.
    """

    return _MatcherWrap(value)


def _check_type(value, types):
    if not isinstance(value, types):
        raise Mismatch.invalid_type(value, types)


def _check_len(value, expected):
    v_len = len(value)
    if v_len != expected:
        raise Mismatch(value, "", f"invalid length - got {v_len}, expected {expected}")


def _match(matcher, value):
    if isinstance(matcher, Matcher):
        return matcher._match(value)

    if isinstance(matcher, dict):
        _check_type(value, dict)
        return _match_dict(matcher, value)

    if matcher == value:
        return
    if matcher is Absent:
        raise Mismatch.unexpected_item(value)
    if value is Absent:
        raise Mismatch.missing_item(value)
    raise Mismatch(value, "", f"{repr(value)} != {repr(matcher)}")


class And(Matcher):
    def __init__(self, *matchers, repr=None):
        self.matchers = matchers
        self._repr = repr

    def __and__(self, other):
        return And(*self.matchers, other)

    def __repr__(self):
        if self._repr is not None:
            return self._repr
        return '&'.join(repr(it) for it in self.matchers)

    def _match(self, other):
        for matcher in self.matchers:
            _match(matcher, other)


class Or(Matcher):
    def __init__(self, *matchers):
        self.matchers = matchers

    def __or__(self, other):
        return Or(*self.matchers, other)

    def __repr__(self):
        return '|'.join(repr(it) for it in self.matchers)

    def _match(self, other):
        mismatches = []
        for matcher in self.matchers:
            try:
                _match(matcher, other)
                return
            except Mismatch as e:
                mismatches.append(e)

        or_str = " nor ".join(repr(i) for i in self.matchers)
        raise Mismatch(other, "", f"is not {or_str}")


class _Any:
    def __repr__(self):
        return "<Any>"

    def __eq__(self, other):
        return other is not Absent


class _Absent:
    def __repr__(self):
        return "<Absent>"

    def __eq__(self, other):
        return other is self


Any = _Any()
Absent = _Absent()


class MayBe(Matcher):
    """ To be used in containers. Item may not exist or must match.
    """

    def __init__(self, v):
        self.v = v

    def __repr__(self):
        return f"MayBe({repr(self.v)})"

    def _match(self, other):
        if self is Absent:
            return
        _match(self.v, other)


def _is_missing(val):
    return not isinstance(val, (MayBe, _Absent))


def _match_dict(matcher: dict, value: dict, allow_unexpected=False):
    missing_keys = set(matcher.keys())
    unexpected_keys = []

    for key, value_v in value.items():
        try:
            matcher_v = matcher[key]
        except KeyError:
            if not allow_unexpected:
                unexpected_keys.append(key)
            continue

        if matcher_v is Absent:
            unexpected_keys.append(key)
            continue

        try:
            _match(matcher_v, value_v)
        except Mismatch as e:
            raise e.prepend(key)

        missing_keys.remove(key)

    missing_keys = sorted(filter(lambda k: _is_missing(matcher[k]), missing_keys))
    if missing_keys:
        raise Mismatch.missing_keys(value, missing_keys)

    if unexpected_keys:
        raise Mismatch.unexpected_keys(value, unexpected_keys)
