from majava.matchers import Matcher, Mismatch, _match


class DictContains(Matcher):
    """ Matches, if a dict contains expected subset of key-value pairs
    """

    def __init__(self, expected, *, recursive=True):
        self.expected = expected
        self.recursive = recursive

    def __repr__(self):
        return f"DictContains({repr(self.expected)})"

    def _match(self, other):
        for k, val in self.expected.items():
            if k not in other:
                raise Mismatch(other, k, f"key '{k}' not found")
            actual_val = other[k]
            try:
                if self.recursive and isinstance(val, dict):
                    val = DictContains(val)
                _match(val, actual_val)
            except Mismatch as e:
                raise e.prepend(k)


class InInterval:
    # The matcher matches, if a given value (other) lies in the interval

    def __init__(self, *value):
        self.first_value, self.second_value = value

    def __eq__(self, other):
        return self.first_value <= other <= self.second_value

    def __repr__(self):
        return f"{self.first_value}, {self.second_value}"


class IsType:
    def __init__(self, *types):
        self.types = types

    def __eq__(self, other):
        return isinstance(other, self.types)

    def __repr__(self):
        return ', '.join(it.__name__ for it in self.types)
