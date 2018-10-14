# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function
import yaml

conf = None


def load(stream):
    global conf
    conf = yaml.load(stream)
