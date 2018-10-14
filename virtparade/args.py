# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function

from virtparade.utils.objects import Singleton


class ArgumentParser(Singleton):
    args = None

    @staticmethod
    def parse(project_name, description, version):
        import argparse

        parser = argparse.ArgumentParser(prog=project_name, description=description, formatter_class=argparse.RawTextHelpFormatter)
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + version)
        subparsers = parser.add_subparsers(dest='subcommand', help='sub-command help')

        # subcommand: run
        parser_run = subparsers.add_parser('run', help='build and run instances')
        parser_run.add_argument('-a', '--all', dest='all', action='store_true', help='build and run all instances')
        parser_run.add_argument('name', nargs='*', help='instance name(s)')

        # subcommand: mount
        parser_mount = subparsers.add_parser('mount', help='mount sepecified instance')
        parser_mount.add_argument('name', nargs=1, help='instance name')

        # subcommand: test
        subparsers.add_parser('test', help='test config file')

        ArgumentParser.args = parser.parse_args().__dict__
        if ArgumentParser.args['subcommand'] is None:  # none subcommand chosen
            parser.print_help()
