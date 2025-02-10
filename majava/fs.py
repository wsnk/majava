from .matchers import Matcher, Mismatch
import os


class _IsDirectory(Matcher):
    def __init__(self, is_empty=None):
        self._is_empty = is_empty

    def __repr__(self):
        if self._is_empty is not None:
            param = "empty" if self._is_empty else "not empty"
            return f"IsDirectory({param})"
        return "IsDirectory"

    def _match(self, other):
        try:
            if not os.path.isdir(other):
                raise Mismatch(other, "", "is not a directory")
        except TypeError as e:
            raise Mismatch(other, "", f"is not a directory (invalid type - {e})") from e

        if self._is_empty is not None:
            is_empty = not os.listdir(other)
            if self._is_empty and not is_empty:
                raise Mismatch(other, "", "directory is not empty")
            if not self._is_empty and is_empty:
                raise Mismatch(other, "", "directory is empty")

    def __call__(self, **kwargs):
        return self.__class__(**kwargs)


IsDirectory = _IsDirectory()
