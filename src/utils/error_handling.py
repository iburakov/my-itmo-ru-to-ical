import logging
from typing import Awaitable, Callable, Iterable, ParamSpec

logger = logging.getLogger(__name__)

P = ParamSpec("P")


def catch_errors_to_empty_iter(func: Callable[P, Awaitable[Iterable]]) -> Callable[P, Awaitable[Iterable]]:
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Iterable:
        try:
            return await func(*args, **kwargs)
        except Exception:
            logger.exception(f"Failed to call {func.__name__}")
            return ()

    return wrapper
