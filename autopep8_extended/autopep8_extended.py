#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import ast
import pep8
import sys

import autopep8

from itertools import tee
import inflection
import re

class Pep8Extended(object):
    def __init__(self, pep8_options, source):
        self.pep8_options = pep8_options
        self.source = source
        # print("EXTENDED pep8_options", pep8_options)

    def get_checks(self):
        msgs = {
            'CW0001': 'Named of class has snake_case style, should'
                ' use CamelCase.',
        }
        return msgs

    def check_cw0001(self):
        # print("self.count", COUNT)
        code = 'CW0001'
        msg = self.get_checks()[code]
        msg += ' Rename from "{old_class_name}" to "{new_class_name}".'
        parsed = ast.parse('\n'.join(self.source))
        class_renamed = {}  # Dict with class names 'old_name: new_name'
        check_result = []
        for node in ast.walk(parsed):
            if isinstance(node, ast.ClassDef):
                node_renamed = inflection.camelize(
                    node.name, uppercase_first_letter=True)
                class_renamed[node.name] = node_renamed
                check_result.append({
                    'id': code,
                    'line': node.lineno,
                    'column': node.col_offset + 1,
                    'info': msg.format(
                        old_class_name=node.name,
                        new_class_name=node_renamed),
                })
            if isinstance(node, ast.Name) \
                and node.id in class_renamed:
                # To replace case where the variable "class_name"
                # is used and change to "ClassName"
                # Examples:
                #   {'myparser': class_name...
                #   method(class_name, parser=class_name)
                #   class_name()
                #   parser=class_name
                check_result.append({
                    'id': code,
                    'line': node.lineno,
                    'column': node.col_offset + 1,
                    'info': msg.format(
                        old_class_name=node.id,
                        new_class_name=node_renamed),
                })
        # import pdb;pdb.set_trace()
        # import pprint
        # print("****************************check_result", pprint.pprint(check_result))
        return check_result

    def _execute_pep8_extendend(self):
        checks = self.get_checks()
        checks_results = []
        for check in checks:
            if check not in self.pep8_options['ignore'] \
                and (not self.pep8_options['select'] \
                    or check in self.pep8_options['select']):
                check_methodname = 'check_' + check.lower()
                if hasattr(self, check_methodname):
                    check_method = getattr(self, check_methodname)
                    check_results = check_method()
                    checks_results.extend(check_results)
        # print("checks_results", checks_results)
        return checks_results
    
COUNT = 0

_execute_pep8_original = autopep8._execute_pep8
def _execute_pep8(pep8_options, source):
    """
    Get all messages error with structure:
    {
        'id': code,
        'line': line_number,
        'column': offset + 1,
        'info': text
    }
    @param pep8_options: dictionary with next structure:
        {
            'ignore': self.options.ignore,
            'select': self.options.select,
            'max_line_length': self.options.max_line_length,
        }
    @param source: Lines of code.
    @return: list with all dict structures
    """
    pep8_ignore = [
        ignore
        for ignore in pep8_options['ignore']
        if not ignore.startswith('C')
    ]
    pep8_select = [
        ignore
        for ignore in pep8_options['select']
        if not ignore.startswith('C')
    ]
    global COUNT
    COUNT+=1
    print(COUNT)
    pep8_original_options = pep8_options.copy()
    pep8_original_options['ignore'] = pep8_ignore
    pep8_original_options['select'] = pep8_select
    res = _execute_pep8_original(pep8_original_options, source)

    pep8_extended = Pep8Extended(pep8_options, source)
    res_extended = pep8_extended._execute_pep8_extendend()
    res.extend(res_extended)
    return res
autopep8._execute_pep8 = _execute_pep8


class FixPEP8(autopep8.FixPEP8):

    def fix_cw0001(self, result):
        regex_msg_old_new = r'\"(?P<old>\w*)(\" to \")(?P<new>\w*)\"'
        match = re.search(regex_msg_old_new, result['info'])
        str_old = match.group('old')
        str_new = match.group('new')
        target = self.source[result['line'] - 1]
        offset = result['column'] - 1
        fixed = target[:offset] + target[offset:].replace(str_old, str_new, 1)
        self.source[result['line'] - 1] = fixed


autopep8.FixPEP8 = FixPEP8


if __name__ == '__main__':
    sys.exit(autopep8.main())
