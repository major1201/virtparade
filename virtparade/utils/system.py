# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import sys
import subprocess


def exec_command(command):
    """
    :return out, err
    """
    import six
    from collections import Iterable

    if isinstance(command, six.string_types):
        _command = [command]
    elif isinstance(command, Iterable):
        _command = list(command)
    else:
        _command = str(command)
    process = subprocess.Popen(_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8'), process.returncode


def exec_command_std(command):
    import six
    from collections import Iterable

    if isinstance(command, six.string_types):
        _command = [command]
    elif isinstance(command, Iterable):
        _command = list(command)
    else:
        _command = str(command)
    process = subprocess.Popen(_command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode


def register_sighandler(handler, *sigs):
    from virtparade.utils import logger

    sig_dict = {
        1: 'SIGHUP',
        2: 'SIGINT',
        3: 'SIGQUIT',
        4: 'SIGILL',
        5: 'SIGTRAP',
        6: 'SIGABRT/SIGIOT',
        7: 'SIGBUS',
        8: 'SIGFPE',
        9: 'SIGKILL',
        10: 'SIGUSR1',
        11: 'SIGSEGV',
        12: 'SIGUSR2',
        13: 'SIGPIPE',
        14: 'SIGALRM',
        15: 'SIGTERM',
        17: 'SIGCHLD/SIGCLD',
        18: 'SIGCONT',
        19: 'SIGSTOP',
        20: 'SIGTSTP',
        21: 'SIGTTIN',
        22: 'SIGTTOU',
        23: 'SIGURG',
        24: 'SIGXCPU',
        25: 'SIGXFSZ',
        26: 'SIGVTALRM',
        27: 'SIGPROF',
        28: 'SIGWINCH',
        29: 'SIGIO/SIGPOLL',
        30: 'SIGPWR',
        31: 'SIGSYS',
        34: 'SIGRTMIN',
        64: 'SIGRTMAX'
    }

    def _sig_proxy(signum, frame):
        try:
            logger.info('Signal: ' + sig_dict.get(signum, 'UNKNOWN') + '(' + str(signum) + ')')
        except:
            pass
        handler()

    import signal
    for sig in sigs:
        try:
            signal.signal(sig, _sig_proxy)
        except ValueError:
            logger.info('Unsupported signal: ' + sig_dict.get(sig, 'UNKNOWN') + '(' + str(sig) + ')')
