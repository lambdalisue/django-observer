# Python 2.7 has an importlib with import_module; for older Pythons,
# Django's bundled copy provides it.
try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module

try:
    from functools import lru_cahce
except ImportError:
    # use pylru instead
    from pylru import lrudecorator as lru_cache
