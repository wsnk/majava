import pytest
from .matchers import Matcher


def pytest_assertrepr_compare(config: pytest.Config, op, left, right):
    if not (isinstance(left, Matcher) or isinstance(right, Matcher)):
        return

    matcher = left if isinstance(left, Matcher) else right

    return [
        f"{left} {op} {right}",
        f"{matcher._mismatch}",
    ]
