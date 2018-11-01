#! /usr/bin/env python3
# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

import os
import sys

from virtparade import VirtParade, VirtParadeError
from virtparade.args import ArgumentParser
from virtparade.utils import setting, logger


def main():
    # init setting
    the_conf_dir = None
    for conf_dir in ('/etc/virtparade', os.path.join(os.path.dirname(__file__), '..', 'virtparade-config-sample')):
        conf_file = os.path.join(conf_dir, 'config.yml')
        if os.path.isfile(conf_file):
            with open(conf_file) as _f:
                setting.load(_f)
                the_conf_dir = os.path.abspath(conf_dir)
            break

    # init logger
    logger.initialize({
        'stdout': {'enable': True},
        'file': {'enable': False},
        'project_name': 'virtparade',
    })

    if the_conf_dir is None:
        logger.error('no config loaded, quit')
        sys.exit(1)

    ArgumentParser.parse('virtparade', 'virtparade, a host virt manager', '0.1.1')
    args = ArgumentParser.args

    try:
        virt_parade = VirtParade(the_conf_dir)
        if args['subcommand'] == 'run':
            if args['all']:
                virt_parade.mkinstances()
            elif len(args['name']) > 0:
                virt_parade.mkinstances(*args['name'])
        elif args['subcommand'] == 'mount':
            virt_parade.mkinstances(*args['name'], step_to='mount')
        elif args['subcommand'] == 'test':
            logger.info('Config dir(%s) test successfully.' % the_conf_dir)
    except VirtParadeError as e:
        logger.error(e, 'virtparade')
    except:
        logger.error_traceback('virtparade')


if __name__ == '__main__':
    main()
