import pytest
import logging
from contextlib import contextmanager


def check_assertion_reason(raises_ctx, expected_reason):
    msg = str(raises_ctx.value)
    logging.debug("Error message: %s", msg)

    reason_ln = msg.rsplit("\n", 1)[-1].strip()
    if reason_ln != expected_reason:
        raise AssertionError(
            "reason line missmatch:\n"
            f"expected: {expected_reason}\n"
            f"actual:   {reason_ln}"
        ) from None


@contextmanager
def raises_assertion_error(reason=None):
    with pytest.raises(AssertionError) as rc:
        yield rc
    if reason is not None:
        check_assertion_reason(rc, reason)
