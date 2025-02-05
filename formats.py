from .matchers import Matcher, Mismatch, _match
import json


class FromJson(Matcher):
    def __init__(self, expected=None):
        self.expected = expected

    def __repr__(self):
        return f"IsJson({repr(self.expected)})"

    def _match(self, other):
        try:
            other_obj = json.loads(other)
        except TypeError as e:
            raise Mismatch(other, "FromJSON()", f"invalid type - {e}")
        except json.JSONDecodeError as e:
            raise Mismatch(other, "FromJSON()", f"invalid JSON - {e}")
        try:
            _match(self.expected, other_obj)
        except Mismatch as e:
            raise e.prepend("FromJSON()")
