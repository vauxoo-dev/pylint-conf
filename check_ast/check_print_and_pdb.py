#!/usr/bin/env python

import ast
import sys
import os
import logging

from colorized_log import main_func

"""
This script check py file for no get "print" or "pdb" sentence.
"""

def check_custom_lint(dir_path):
    for dirname, dirnames, filenames in os.walk(dir_path):
        print "dirname, dirnames, filenames",dirname, dirnames, filenames
        for filename in filenames:
            fext = os.path.splitext(filename)[1]
            if fext == '.py':
                fname_path = os.path.join(dirname, filename)
                try:
                    with open(fname_path) as fin:
                        parsed = ast.parse(fin.read())
                except:
                    parsed = None
                    pass
                if parsed:
                    for node in ast.walk(parsed):
                        if isinstance(node, ast.Print):
                            #if "print" sentence then add a out
                            #print '"print" at line {} col {} file {}'.format(node.lineno, node.col_offset, fname_path)
                            logging.warning( '{}:{}: [print sentence] "print" sentence detected'.format(\
                                fname_path, node.lineno) )
                        elif isinstance(node, ast.Import):
                            for import_name in node.names:
                                if import_name.name == 'pdb':
                                    #if "print" sentence then add a out
                                    logging.warning( '{}:{}: [import pdb sentence] "import pdb" sentence detected'.format(\
                                fname_path, node.lineno) )


def main():
    if len( sys.argv ) == 2 and os.path.isdir(sys.argv[1]):
        check_custom_lint(sys.argv[1])
    else:
        logging.warning("First param should be directoy path to check")

if __name__ == '__main__':
    exit(main())
