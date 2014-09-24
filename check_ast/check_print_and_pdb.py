import ast
import sys

"""
This script check py file for no get "print" or "pdb" sentence.
"""
#dirname of file py to check
dirname = sys.argv[1]

fname = sys.argv[1]

for dirname, dirnames, filenames in os.walk(path):
    for filename in filenames:
        fname_path = os.path.join(dirname, filename)
        if os.path.splitext(fname_path)[1] == '.py':
            with open(fname_path) as fin:
                parsed = ast.parse(fin.read())
        else:
            continue

for node in ast.walk(parsed):
    if isinstance(node, ast.Print):
        #if "print" sentence then add a out
        print '"print" at line {} col {}'.format(node.lineno, node.col_offset)
    elif isinstance(node, ast.Import):
        for import_name in node.names:
            if import_name.name == 'pdb':
                #if "print" sentence then add a out
                print '"import pdb" at line {} col {}'.format(node.lineno, node.col_offset)



for path_test in paths_to_test:
            for paths_py in _get_paths_py_to_test(path_test):
                with open(paths_py) as fin:
                    parsed = ast.parse(fin.read())
                for node in ast.walk(parsed):
                    if build.pylint_config.check_print and isinstance(node, ast.Print):
                        message = '"print" at line {} col {} of file: %s'.format(node.lineno, node.col_offset)%paths_py
                        self.pool['ir.logging'].create(cr, uid, {
                                                                'build_id': build.id,
                                                                'level': 'WARNING',
                                                                'type': 'runbot',
                                                                'name': 'odoo.runbot',
                                                                'message': message,
                                                                'path': paths_py,
                                                                'func': 'Detect print',
                                                                'line': node.lineno,
                                                            }, context=context)
                    elif build.pylint_config.check_pdb and isinstance(node, ast.Import):
                        for import_name in node.names:
                            if import_name.name == 'pdb':
                                message = '"import pdb" at line {} col {} of file: %s'.format(node.lineno, node.col_offset)%paths_py
                                self.pool['ir.logging'].create(cr, uid, {
                                                                'build_id': build.id,
                                                                'level': 'WARNING',
                                                                'type': 'runbot',
                                                                'name': 'odoo.runbot',
                                                                'message': message,
                                                                'path': paths_py,
                                                                'func': 'Detect pdb',
                                                                'line': node.lineno,
                                                            }, context=context)