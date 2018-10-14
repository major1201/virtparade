# encoding: utf-8
from __future__ import division, absolute_import, with_statement, print_function


def parse_j2_file(template_file, **kwargs):
    with open(template_file) as f:
        return parse_j2(f.read(), **kwargs)


def parse_j2_file_to_file(template_file, output_file, **kwargs):
    with open(output_file, 'w') as f:
        f.write(parse_j2_file(template_file, **kwargs))


def parse_j2(template_text, **kwargs):
    from jinja2 import Template

    template = Template(template_text)
    return template.render(kwargs)
