from majava.matchers import Matcher, Mismatch, _match_dict


class DictContains(Matcher):
    """ Matches, if a dict contains expected subset of key-value pairs
    """

    def __init__(self, expected, *, recursive=True):
        self.expected = expected
        self.recursive = recursive

    def __repr__(self):
        return f"DictContains({repr(self.expected)})"

    def _match(self, other):
        _match_dict(self.expected, other, allow_unexpected=True)


class InInterval(Matcher):
    def __init__(self, low, high):
        self.low, self.high = low, high

    def __repr__(self):
        return f"InInterval({self.low}, {self.high})"

    def _match(self, other):
        if not (self.low <= other <= self.high):
            raise Mismatch(other, "", f"not {self}")


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
