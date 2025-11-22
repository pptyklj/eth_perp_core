import time
from typing import Callable


def rate_limited(min_interval: float):
    def decorator(func: Callable):
        last_call = 0.0

        def wrapper(*args, **kwargs):
            nonlocal last_call
            now = time.time()
            elapsed = now - last_call
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_call = time.time()
            return result

        return wrapper

    return decorator
