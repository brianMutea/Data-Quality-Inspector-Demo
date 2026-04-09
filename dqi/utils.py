"""Utility functions for DataQualityInspector."""

import time
from functools import wraps


def timed(func):
    """
    Decorator that measures and prints the execution time of a function.
    
    Args:
        func: The function to be timed
        
    Returns:
        Wrapped function that prints elapsed time after execution
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"{func.__name__} completed in {elapsed_time:.2f} seconds")
        return result
    return wrapper
