from majava.matchers import Matcher, Mismatch, _match_dict, make_matcher, _match, Absent


class DictContains(Matcher):
    """ If value contains expected key-value pairs
    """

    def __init__(self, expected, *, recursive=True):
        self.expected = expected
        self.recursive = recursive

    def __repr__(self):
        return f"DictContains({repr(self.expected)})"

    def _match(self, other):
        _match_dict(self.expected, other, allow_unexpected=True)


class IsInstance(Matcher):
    def __init__(self, *types):
        self.types = types

    def _types_str(self):
        return "|".join(i.__name__ for i in self.types)

    def __repr__(self):
        return f"IsInstance({self._types_str()})"

    def _match(self, other):
        if not isinstance(other, self.types):
            raise Mismatch(other, "", f"not {self}")


class Round(Matcher):
    def __init__(self, value, digits=0):
        self.value = round(value, digits)
        self.digits = digits

    def __repr__(self):
        return f"Round({self.value})"

    def _match(self, other):
        if self.value != round(other, self.digits):
            raise Mismatch(other, "", f"not ~{self.value}")


class ContainsOrdered(Matcher):
    def __init__(self, items):
        self.items = items

    def __repr__(self):
        return f"ContainsOrdered({self.items})"

    def _match(self, other):
        idx = 0
        for it in self.items:
            try:
                idx = other[idx:].index(it) + 1
            except ValueError:
                raise Mismatch(other, "", f"{repr(it)} is not in order")


class _Contains(Matcher):
    def __init__(self, items, ordered=False):
        self.items = items
        self.ordered = ordered

    def __repr__(self):
        return f"Contains({self.items})"

    def _match(self, other):
        missing_items = []
        for it in self.items:
            if it not in other:
                missing_items.append(it)

        if missing_items:
            raise Mismatch.missing_items(other, missing_items)


class Unordered(_Contains):
    """ Value must contains all expected items in any order
    """

    def __repr__(self):
        return f"Unordered({self.items})"

    def _match(self, other):
        if len(self.items) != len(other):
            raise Mismatch(other, "", f"len is not {len(self.items)}")
        super()._match(other)


def Contains(items, ordered=False):
    if ordered:
        return ContainsOrdered(items)
    return _Contains(items)


@make_matcher
def StartsWith(value, expected):
    return value.startswith(expected)


@make_matcher
def EndsWith(value, expected):
    return value.endswith(expected)


@make_matcher
def LengthIs(value, expected):
    return len(value) == expected


@make_matcher
def InInterval(value, low, high):
    return low <= value <= high


@make_matcher
def HasAttrs(value, **kwargs):
    for key, expected in kwargs.items():
        try:
            _match(expected, getattr(value, key, Absent))
        except Mismatch as e:
            raise e.prepend(key)
    return True
