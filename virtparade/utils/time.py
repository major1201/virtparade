# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

FMT_DATE = '%Y-%m-%d'
FMT_TIME = '%H:%M:%S'
FMT_TIME_EXACT = '%H:%M:%S.%f'
FMT_DATETIME = '%Y-%m-%d %H:%M:%S'
FMT_DATETIME_EXACT = '%Y-%m-%d %H:%M:%S.%f'


def now(fmt=None):
    from datetime import datetime
    _now = datetime.now()
    if fmt is None:
        return _now
    return _now.strftime(fmt)


def utcnow(fmt=None):
    from datetime import datetime
    _now = datetime.utcnow()
    if fmt is None:
        return _now
    return _now.strftime(fmt)


def format_date(date, fmt, default=None):
    try:
        return date.strftime(fmt)
    except:
        return default


def string_to_date(date_string, fmt, default=None):
    from datetime import datetime
    try:
        return datetime.strptime(date_string, fmt)
    except:
        return default
