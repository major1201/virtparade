# encoding= utf-8
from __future__ import division, absolute_import, with_statement, print_function


def contains(exp, *values):
    for value in values:
        if exp == value:
            return True
    return False


def is_function(f):
    return hasattr(f, "__call__")


def first(*lst):
    if len(lst) > 0:
        return lst[0]
    return None


def combine(items, n=1):
    r = []
    if n == 1:
        for it in items:
            r.append(it)
    else:
        if len(items) > n:
            for pos in range(len(items) - n + 1):
                v1 = items[pos]
                v2 = combine(items[pos + 1:], n - 1)
                for it in v2:
                    if isinstance(it, list):
                        v = it
                        v.insert(0, v1)
                        r.append(v)
                    else:
                        r.append([v1, it])
        else:
            v = []
            for it in items:
                v.append(it)
            r.append(v)
    return r


class _Singleton(type):
    """ A metaclass that creates a Singleton base class when called. """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Singleton(_Singleton('SingletonMeta', (object,), {})):
    pass
