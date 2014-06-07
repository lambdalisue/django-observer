#!/usr/bin/env python
# vim: set fileencoding=utf8 :
"""Singleton Mixin"""


class Singleton(object):
    """Singleton Mixin Class

    Inherit this class and make the subclass Singleton.

    Usage:
        >>> class A(object):
        ...     pass
        >>> class B(Singleton):
        ...     pass
        >>> a1 = A()
        >>> a2 = A()
        >>> b1 = B()    # Create instance as usual
        >>> b2 = B()
        >>> a1 == a2    # a1, a2 are not singleton
        False
        >>> b1 == b2    # b1, b2 are singleton
        True

    Reference:
        http://d.hatena.ne.jp/BetaNews/20090607/1244358178
    """
    def __new__(cls, *args, **kwargs):
        # Store instance on cls._instance_dict with cls hash
        key = str(hash(cls))
        if not hasattr(cls, '_instance_dict'):
            cls._instance_dict = {}
        if key not in cls._instance_dict:
            cls._instance_dict[key] = \
                super(Singleton, cls).__new__(cls, *args, **kwargs)
        return cls._instance_dict[key]


if __name__ == '__main__':
    # Run doctest
    import doctest
    doctest.testmod()
