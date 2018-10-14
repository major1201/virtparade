# encoding= utf-8
from __future__ import division, absolute_import, with_statement, print_function


def format_size(size, base_unit='B'):
    size = float(size)
    rank = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    if base_unit not in rank:
        raise ValueError('The base_unit not correct.')
    rank = rank[rank.index(base_unit):]
    c = 0
    while size >= 1000 and c < len(rank) - 1:
        size /= 1024
        c += 1
    return size, rank[c]


def safe_int(o, default=0):
    ret = default
    try:
        ret = int(o)
    finally:
        return ret


def safe_float(o, default=0.0):
    ret = default
    try:
        ret = float(o)
    finally:
        return ret
