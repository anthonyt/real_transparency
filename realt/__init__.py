import functools
import logging

log = logging.getLogger(__name__)

def memoize(func):
    """
    A simple memoization decorator.

    Caches calls to the wrapped function using a tuple of the args and a frozen
    set of the kwargs.

    Adds a func.clear_cache() function for erasing the memoization cache.

    XXX: For function func(a), func(1) and func(a=1) will refer to different
         cached results.
    """
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = args, frozenset(kwargs.iteritems())
        if key in cache:
            log.debug('Returning cached value for %s(%r, %r)', func.__name__, *args, **kwargs)
            return cache[key]
        else:
            cache[key] = result = func(*args, **kwargs)
            return result

    wrapper._cache = cache
    wrapper.clear_cache = wrapper._cache.clear

    return wrapper

