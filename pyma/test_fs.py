class InInterval:
    # The matcher matches, if a given value (other) lies in the interval

    def __init__(self, *value):
        self.first_value, self.second_value = value

    def __contains__(self, other):
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


class LikeDict:
    def __init__(self, val):
        self.val = val

    def __eq__(self, other):
        for k, v in self.val.items():
            if other[k] != v:
                return False
        return True

    def __repr__(self):
        return repr(self.val)


def test_ininterval():
    assert 7 in InInterval(1, 7)
    assert 10 not in InInterval(1, 7)


def test_istype():
    assert 2 != IsType(str)
    assert 2 == IsType(int, str)
    assert "b" == IsType(int, str)
    assert "b" != IsType(int)
    assert "b" == IsType(str)
