"""Utility functions for DataQualityInspector."""

import time
from functools import wraps

from dqi.console import console


def timed(func):
    """
    Decorator that measures and prints the execution time of a function.

    Output uses Rich dim styling so timings sit quietly beside progress UI.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        console.print(f"[dim]{func.__name__} completed in {elapsed_time:.2f}s[/dim]")
        return result

    return wrapper
