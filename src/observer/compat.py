# Python 2.7 has an importlib with import_module; for older Pythons,
# Django's bundled copy provides it.
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    from functools import lru_cahce
except ImportError:
    try:
        # use pylru instead
        from pylru import lrudecorator as lru_cache
    except ImportError:
        # use pylru is not installed
        def lru_cache(maxsize):
            def inner(fn):
                return fn
            return inner
