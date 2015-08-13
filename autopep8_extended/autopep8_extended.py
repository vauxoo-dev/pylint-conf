#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import ast
import re
import sys

import autopep8
import inflection


class Pep8Extended(object):
    def __init__(self, pep8_options, source):
        self.pep8_options = pep8_options
        self.source = source

    def get_checks(self):
        msgs = {
            'CW0001': 'Named of class has snake_case style, should'
                      ' use CamelCase. Change of "{old_class_name}"'
                      ' to "{new_class_name}" next (lines,columns):'
                      ' {lines_columns}',
        }
        return msgs

    def check_cw0001(self):
        code = 'CW0001'
        msg = self.get_checks()[code]
        class_renamed = {}
        check_result = []

        # Fix 'SyntaxError: encoding declaration in Unicode string'
        parsed_source = self.source
        line_deleted = False
        if len(parsed_source) >= 1 and \
           ('# -*- coding:' in parsed_source[0] or
           '# -*- encoding:' in parsed_source[0]):
            parsed_source = parsed_source[1:]
            line_deleted = True
        elif len(parsed_source) >= 2 and \
            ('# -*- coding:' in parsed_source[1] or
             '# -*- encoding:' in parsed_source[1]):
            parsed_source = parsed_source[0:1] + parsed_source[2:]
            line_deleted = True
        parsed = ast.parse(''.join(parsed_source))

        renamed_names = []
        for node in ast.walk(parsed):
            if isinstance(node, ast.ClassDef):
                node_renamed = inflection.camelize(
                    node.name, uppercase_first_letter=True)
                renamed_names.append(node_renamed)
                if node_renamed != node.name:
                    class_renamed.setdefault(
                        node.name, {'line_col': []})
                    class_renamed[node.name]['renamed'] = \
                        node_renamed
                    class_renamed[node.name]['line_col'].append((
                        node.lineno + line_deleted,
                        node.col_offset + 1))
            if isinstance(node, ast.Name) \
               and node.id in class_renamed:
                class_renamed[node.id]['line_col'].append((
                    node.lineno + line_deleted, node.col_offset + 1))
        if len(set(renamed_names)) != len(renamed_names):
            # Avoid errors when you have duplicated class name
            # but with different style in same file.
            # e.g. class my_class_1() and class MyClass1()
            print(
                "Waning: Aborted. You have two class named "
                "my_name and MyName in a same file.\n"
                "Review your next class names: "
                "{0}".format(renamed_names)
            )
            return check_result

        for class_original_name in class_renamed:
            line, column = class_renamed[
                class_original_name]['line_col'][0]
            check_result.append({
                'id': code,
                'line': line,
                'column': column,
                'info': msg.format(
                    old_class_name=class_original_name,
                    new_class_name=class_renamed[
                        class_original_name]['renamed'],
                    lines_columns=class_renamed[
                        class_original_name]['line_col']
                ),
            })
        return check_result

    def _execute_pep8_extendend(self):
        checks = self.get_checks()
        checks_results = []
        for check in checks:
            if check not in self.pep8_options['ignore'] \
               and (not self.pep8_options['select']
               or check in self.pep8_options['select']):
                check_methodname = 'check_' + check.lower()
                if hasattr(self, check_methodname):
                    check_method = getattr(self, check_methodname)
                    check_results = check_method()
                    checks_results.extend(check_results)
        return checks_results


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
    pep8_extended_obj = Pep8Extended(pep8_options, source)
    res_extended = pep8_extended_obj._execute_pep8_extendend()
    res = _execute_pep8_original(pep8_options, source)
    res.extend(res_extended)
    return res


autopep8._execute_pep8 = _execute_pep8


class FixPEP8(autopep8.FixPEP8):

    def fix_cw0001(self, result):
        '''
        Replace class name from snake_case to CamelCase
        :param result: Dict with next values
            {
            'id': code,
            'line': line_number,
            'column': column_number,
            'info': 'Named of class has snake_case style, should'
                    ' use CamelCase. Change of "{old_class_name}"'
                    ' to "{new_class_name}" next (lines,columns):'
                    ' {lines_columns}'
            }
            Where info keys values {old_class_name} to replace,
            {new_class_name} is new class name,
            {lines_columns} is a list of lines, columns
            with invokes to {old_class_name}.
        :return: Return list of integer with value of # line modified
        '''
        regex_old_new = r'\"(?P<old>\w*)(\" to \")(?P<new>\w*)\"'
        match_old_new = re.search(regex_old_new, result['info'])
        regex_lc = r"(?P<lines_columns>\[[\(\d, \)]*\])"
        match_lc = re.search(regex_lc, result['info'])
        if not match_lc or not match_old_new:
            return []
        str_old = match_old_new.group('old')
        str_new = match_old_new.group('new')
        lines_columns = ast.literal_eval(
            match_lc.group('lines_columns'))
        lines_modified = []
        for line, column in lines_columns:
            target = self.source[line - 1]
            offset = column - 1
            fixed = target[:offset] + target[offset:].replace(
                str_old, str_new, 1)
            self.source[line - 1] = fixed
            lines_modified.append(line)
        return lines_modified


autopep8.FixPEP8 = FixPEP8


if __name__ == '__main__':
    sys.exit(autopep8.main())
