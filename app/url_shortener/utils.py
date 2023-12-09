from typing import Callable, Optional, TypeVar


_T = TypeVar("_T")
_U = TypeVar("_U")


def fmap(value: Optional[_T], fn: Callable[[_T], Optional[_U]]) -> Optional[_U]:
    """Applies a given function to a value if it is not None and return the result."""
    if value is None:
        return None
    return fn(value)
