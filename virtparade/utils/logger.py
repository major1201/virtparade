# encoding=utf-8
from __future__ import division, absolute_import, with_statement, print_function
import logging

DEFAULT_LOGGER_NAME = 'SYS'
DEFAULT_LOGGING_FMT = '[%(asctime)s %(levelname)s %(name)s] %(message)s'
DEFAULT_LOGGIN_LEVEL = logging.NOTSET


def initialize(conf):
    import os
    import sys
    import logging.handlers
    from collections import Iterable
    from virtparade.utils import num, strings

    _logger = logging.getLogger()

    # stream logger
    config_stdout = conf.get('stdout', {})
    if config_stdout.get('enable'):
        _stream_handler = logging.StreamHandler(sys.stdout)
        _stream_handler.setFormatter(logging.Formatter(strings.get_non_empty_str(config_stdout, 'format', DEFAULT_LOGGING_FMT)))
        _stream_handler.setLevel(num.safe_int(config_stdout.get('level'), DEFAULT_LOGGIN_LEVEL))
        _logger.addHandler(_stream_handler)

    # file logger
    config_file = conf.get('file', {})
    if config_file.get('enable'):
        path = strings.get_non_empty_str(config_file, 'path',
                                         os.path.join(os.path.dirname(__file__), '..', conf.get('project_name') + ".log")
                                         )
        config_rotating = config_file.get('rotating', {})
        if config_rotating.get('enable'):
            _file_handler = logging.handlers.TimedRotatingFileHandler(path,
                                                                      when=config_rotating.get('when', 'H'),
                                                                      backupCount=config_rotating.get('backup_count', 0),
                                                                      encoding='utf-8')
        else:
            _file_handler = logging.handlers.RotatingFileHandler(path, encoding='utf-8')
        _file_handler.setFormatter(logging.Formatter(strings.get_non_empty_str(config_file, 'format', DEFAULT_LOGGING_FMT)))
        _file_handler.setLevel(num.safe_int(config_file.get('level'), DEFAULT_LOGGIN_LEVEL))
        _logger.addHandler(_file_handler)

    _logger.setLevel(DEFAULT_LOGGIN_LEVEL)

    loggers = conf.get('loggers')
    if loggers is not None:
        assert isinstance(loggers, Iterable)
        for item in loggers:
            _log = logging.getLogger(item.get('name'))
            if 'level' in item:
                _log.setLevel(num.safe_int(item.get('level'), DEFAULT_LOGGIN_LEVEL))


def critical(msg, name=DEFAULT_LOGGER_NAME):
    logging.getLogger(name).critical(msg)


def error(msg, name=DEFAULT_LOGGER_NAME):
    logging.getLogger(name).error(msg)


def warning(msg, name=DEFAULT_LOGGER_NAME):
    logging.getLogger(name).warning(msg)


def info(msg, name=DEFAULT_LOGGER_NAME):
    logging.getLogger(name).info(msg)


def debug(msg, name=DEFAULT_LOGGER_NAME):
    logging.getLogger(name).debug(msg)


def error_traceback(name=DEFAULT_LOGGER_NAME):
    import traceback
    format_exc = traceback.format_exc()
    error(format_exc, name)
    return format_exc
