#!/usr/bin/env python
import os
import sys
import ast
import subprocess

import inflection

ALL_FIXES = [
    'fix_unused_import',
    'fix_unused_var',
    'fix_autopep8',
    'fix_trailing_whitespace',
    'remove_linenos_pylint_w0104', #  Statement seems to have no effect
    'remove_linenos_pylint_w0404', #  reimported
    'fix_relative_import',
    'fix_sort_import',
    'rm_dummy_class_invoke',
    'snake_case2CamelCase',
]

"""
This is the script to fix all cases: ALL_FIXES
Run this script with
python replace_import.py PATH_YOUR_MODULE all

@sys.argv[1]: path of dirname with all python packages.
@sys.argv[2]: test to run. Use "all" for all fixes or a element of ALL_FIXES

This script required:
sudo pip install autoflake pylint isort 3to2 autopep8
sudo apt-get install sed
"""

def run(l, env=None):
    """Run a command described by l in environment env"""
    #log("run", l)
    env = dict(os.environ, **env) if env else None
    if isinstance(l, list):
        print "run lst",' '.join( l )
        #import pdb;pdb.set_trace()
        if env:
            rc = os.spawnvpe(os.P_WAIT, l[0], l, env)
        else:
            rc = os.spawnvp(os.P_WAIT, l[0], l)
    elif isinstance(l, str):
        print "run str", l
        tmp = ['sh', '-c', l]
        if env:
            rc = os.spawnvpe(os.P_WAIT, tmp[0], tmp, env)
        else:
            rc = os.spawnvp(os.P_WAIT, tmp[0], tmp)
    #log("run", rc=rc)
    return rc
"""
def run_cmd_pyfile_bkp(l, env=None):
    run(l, env=env)
"""
def run_output(l, cwd=None):
    #log("run_output",l)
    #print "run output:", ' '.join( l ), "into", cwd
    return subprocess.Popen(l, stdout=subprocess.PIPE, cwd=cwd).communicate()[0]

def multi_getattr(obj, attr, default=None):
    """
    Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.

    """
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            #if default:
            return default
            #else:
               # raise
    return obj

def get_node_fc_data(node):
    args = multi_getattr(node, "value.args")
    args_str = ''
    if isinstance(args, list):
        args_str = ','.join([arg.s for arg in args if hasattr(args, 's')])
    code_data_line = {
        'lineno': node.lineno if hasattr(node, 'lineno') else None,
        'col_offset': node.col_offset if hasattr(node, 'col_offset') else None,
        'node': node,
        'code': "{}.{}.{}('{}')".format( multi_getattr(node, "value.func.value.value.id"), \
        multi_getattr(node, "value.func.value.attr"), \
        multi_getattr(node, "value.func.attr"), \
        args_str),
    }
    return code_data_line



def pool_get_wo_assigned(fdata, func_name_list=None):
    try:
        parsed = ast.parse(fdata)
    except:
        parsed = None
    code_data_lines = []
    if func_name_list is None:
        func_name_list = []
    if parsed:
        for node in ast.walk(parsed):
          #print multi_getattr(node, "lineno")
          #linenos.append(multi_getattr(node, "lineno"))
          #if multi_getattr(node, "lineno") == 41:
           #if isinstance( node, ast.Expr ) and isinstance( multi_getattr(node, "value"), ast.Call):
            #import pdb;pdb.set_trace()
            if isinstance( node, ast.Expr ) and isinstance( multi_getattr(node, "value"), ast.Call):
                if multi_getattr(node, "value.func.value.value.id") == 'self' and\
                        multi_getattr(node, "value.func.value.attr") == 'pool' and\
                        multi_getattr(node, "value.func.attr") == 'get':
                    code_data_line = get_node_fc_data(node)
                    code_data_lines.append( code_data_line )
                    #TODO: Check netsvc.LocalService
                elif multi_getattr(node, "value.func.attr") == 'copy' and\
                        multi_getattr(node, "value.func.value.id") == 'context':
                    code_data_line = get_node_fc_data(node)
                    code_data_lines.append( code_data_line )
                elif multi_getattr(node, "value.func.attr") in func_name_list:
                    code_data_line = get_node_fc_data(node)
                    code_data_lines.append( code_data_line )
            #if isinstance( node, ast.Expr ) and isinstance( multi_getattr(node, "value"), ast.Subscript):
                #result['context'] #node.value.slice.value.s --> context
                                   #node.value.value.id --> result
                pass
    #print sorted(list(set(linenos)))
    return code_data_lines

def compile_ok(fname_path):
    try:
        compile(open(fname_path).read(), fname_path, "exec")
        return True
    except:
        pass
    return False

def delete_linenos(fname_path, linenos_list):
    compile_result = None
    if linenos_list:
        linenos_to_delete_cmd = 'd;'.join( \
            [str(item) for item in linenos_list] ) + 'd'
        cmd_sed = ["sed", "-i.bkp", "-e", linenos_to_delete_cmd, fname_path]
        run(cmd_sed)
        compile_result = compile_ok(fname_path)
        if compile_result:
            os.remove(fname_path + ".bkp")
        else:
            os.rename(fname_path + ".bkp", fname_path)
    return compile_result
'''
def pack_local_ok(packname, path):
    if os.path.isfile(path):
        dirname = os.path.dirname(path)
    elif os.path.isdir(path):
        dirname = path
    else:
        raise "This path is not a file or directory"
    if os.path.isfile( os.path.join(dirname, packname + '.py') )\
            or os.path.isfile( os.path.join(dirname, packname, '__init__.py')):
        return True
    return False

def get_pack_from_astnode(ast_node):
    pack_names = []
    if isinstance(ast_node, ast.Import):
        pack_names.extend([pack.name for pack in multi_getattr(ast_node, "names")])
    elif isinstance(ast_node, ast.ImportFrom):
        pack_from_import = multi_getattr(ast_node, "module")
        if pack_from_import:
            pack_names.append(pack_from_import)
    return pack_names

def get_convert_import_relative_astnode(pack_names_list):
    old_import = "import {}".format(", ".join(pack_names_list))
    new_import = "from . import {}".format(", ".join(pack_names_list))
    return [old_import, new_import]

def file_change_line(fname, old_new_import, lineno):
    run(["sed", "-i.bkp", "-e",str(lineno) + "s/"+ old_new_import[0] + "/" + old_new_import[1] + "/", fname])

def search_relative_imports(path):
    """
    This method is used to search relative imports in py files.

    :param paths: Path of py files to check relative imports.
    """
    with open(path) as fin:
        parsed = ast.parse(fin.read())
    for node in ast.walk(parsed):
        pack_names = get_pack_from_astnode(node)
        pack_names_local_ok = [pack_local_ok(pack_name, path) for pack_name in pack_names]
        if any(pack_names_local_ok):
            old_new_import = get_convert_import_relative_astnode(pack_names)
            file_change_line(path, old_new_import, node.lineno)
        else:
            continue
'''
def get_pylint_error_linenos(fname_path, error_list):
    if isinstance(error_list, str) or isinstance(error_list, basestring):
        error_list = error_list and [error_list] or []
    linenos = []
    if error_list:
        cmd_error_list = []
        for error_str in error_list:
            cmd_error_list.extend(['-e', error_str])
        cmd = ["pylint", "-d", "all"] + cmd_error_list + \
              ["-r", "n", '--msg-template="{line}"', fname_path]
        pylint_out = run_output(cmd)
        linenos = [int(s) for s in pylint_out.split() if s.isdigit()]
    return linenos

def remove_trailing_whitespace(fname_path):
    compile_result = None
    cmd_sed = ["sed", "-i.bkp", 's/[ \t]*$//', fname_path]
    run(cmd_sed)
    compile_result = compile_ok(fname_path)
    if compile_result:
        os.remove(fname_path + ".bkp")
    else:
        os.rename(fname_path + ".bkp", fname_path)
    return compile_result

def fix_relative_import(fname_path):
    compile_result = None
    fname_path_bkp = fname_path + '.bak'
    cmd = ["2to3", "--no-diffs", "-wf", "import", fname_path]
    run(cmd)
    compile_result = compile_ok(fname_path)
    if os.path.isfile(fname_path_bkp):
        if compile_result:
            os.remove(fname_path + ".bak")
        else:
            os.rename(fname_path + ".bak", fname_path)
    return compile_result

def fix_sort_import(fname_path):
    compile_result = None
    fname_path_bkp = fname_path + '.bak'
    cmd = ["isort", fname_path]
    run(cmd)
    compile_result = compile_ok(fname_path)
    if os.path.isfile(fname_path_bkp):
        if compile_result:
            os.remove(fname_path + ".bak")
        else:
            os.rename(fname_path + ".bak", fname_path)
    return compile_result

def replace_str_line(fname, old_str, new_str, lineno):
     run(["sed", "-i.bkp", "-e", str(lineno) + "s/"+ old_str + "/" + new_str + "/", fname])

def rm_dummy_class_invoke(fname_path):
    """
    class eg1:
        pass
    eg1()  # without assing to a variable without parameters-
    After this script you will have your code:
    class eg1:
        pass
    Without eg1()
    """
    class_names = []
    linenos_to_delete = []
    with open(fname_path) as fin:
        parsed = ast.parse(fin.read())
        for node in ast.walk(parsed):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
            if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                if node.func.id in class_names \
                    and len(node.args) == 0 \
                    and node.col_offset == 0:
                    linenos_to_delete.append(node.lineno)
    delete_linenos(fname_path, linenos_to_delete)

def snake_case2CamelCase(fname_path):
    with open(fname_path) as fin:
        parsed = ast.parse(fin.read())
        for node in ast.walk(parsed):
            if isinstance(node, ast.ClassDef):
                node_name = node.name
                node_renamed = inflection.camelize(
                    node.name, uppercase_first_letter=True)
                if node_name != node_renamed:
                    replace_str_line(
                        fname_path, ' ' + node.name, ' ' + node_renamed,
                        node.lineno)
            if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                if node.func.id == 'super':
                    node_name = node.args[0].id
                    node_renamed = inflection.camelize(
                        node.args[0].id, uppercase_first_letter=True)
                    if node_name != node_renamed:
                        # TODO: Validate if is a super of a class renamed.
                        replace_str_line(fname_path, 'super(' + node_name, 'super(' + node_renamed, node.lineno)
                        # if was used super(\nclass_name)
                        replace_str_line(fname_path, node_name + ',', node_renamed + ',', node.lineno + 1)


def fix_custom_lint(dir_path, context=None):
    if context is None:
        context = dict( [(fix, True) for fix in ALL_FIXES])
    for dirname, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
              #if '__unported__' in dirname: continue
              #if 'hr_expense_replenishment/' in dirname and filename == 'hr_expense.py':
              #if 'account_move_line_address' in dirname and filename == 'account_move_line.py':
              #if 'payroll_amount_residual' in dirname and filename == 'hr_payslip.py':
              #if ('account_invoice_tax' in dirname and filename=='account_invoice_tax.py') or \
              #   ('account_voucher_tax' in dirname and filename=='account_voucher.py') or \
              #   ('project_conf' in dirname and filename=='project.py') or \
              #   ('user_story' in dirname and filename=='user_story_report_mako.py') or \
              #   ('user_story' in dirname and filename=='test_user_story.py'):
                fname_woext, fext = os.path.splitext(filename)
                fname_path = os.path.join(dirname, filename)
                #print "fname_path",fname_path
                if fext == '.py':
                    compile_ok_result = compile_ok(fname_path)
                    if not compile_ok_result:
                        print "*"*20,"syntaxis error in file",fname_path#TODO: Make a log warning
                        continue
                    if fname_woext not in ['__init__', '__openerp__', '__terp__']:
                        if context.get('fix_unused_var'):
                            run(["autoflake", "--remove-unused-variables", "-ri", fname_path])

                            with open(fname_path) as fin:
                                fdata = fin.read()
                            lines_pool_get_wo_assigned = pool_get_wo_assigned(fdata, \
                                ['fields_get', 'search', 'browse', 'get', 'LocalService',\
                                    'ServerProxy', 'get_pool'])
                            linenos_to_delete = []
                            for line_pool_get_wo_assigned in lines_pool_get_wo_assigned:
                                lineno = line_pool_get_wo_assigned.get('lineno')
                                linenos_to_delete.append(lineno)
                            delete_linenos(fname_path, linenos_to_delete)

                        if context.get('fix_unused_import'):
                            run(["autoflake", "--remove-all-unused-imports", "-ri", fname_path])
                            #with open(fname_path) as fin:
                            #    fdata = fin.read()
                            #TODO: Only re-save it if was modify
                            #with open(fname_path, "w") as fin:
                            #    fin.write( fdata )

                    error_list = []
                    #Statement seems to have no effect
                    if context.get('remove_linenos_pylint_w0104') and\
                        fname_woext != '__openerp__':
                        error_list.append('w0104')
                    #Reimport
                    if context.get('remove_linenos_pylint_w0404'):
                        error_list.append('w0404')
                    if error_list:
                        linenos_to_delete = get_pylint_error_linenos(\
                            fname_path, error_list)
                        delete_linenos(fname_path, linenos_to_delete)


                    if context.get('fix_autopep8'):
                        open(fname_path + '.bkp', "w").write(
                             open(fname_path, "r").read() )
                        #Ignore fix max-line-length and continuation line
                        #  under-indented for visual indent. 
                        #  We have mute this errors in our pylint
                        run(["autopep8", "-i", "--ignore", "E501,E128", fname_path])
                        compile_ok_result = compile_ok(fname_path)
                        if compile_ok_result:
                            os.remove(fname_path + ".bkp")
                        else:
                            os.rename(fname_path + ".bkp", fname_path)


                    if context.get('fix_trailing_whitespace'):
                        remove_trailing_whitespace(fname_path)

                    if context.get('fix_relative_import'):
                        fix_relative_import(fname_path)

                    if context.get('fix_sort_import'):
                        fix_sort_import(fname_path)

                    if context.get('snake_case2CamelCase'):
                        snake_case2CamelCase(fname_path)
                    # TODO: Change <> by !=
                    #       find . -type f -name "*.py" -exec sed -i 's/<>/\!\=/g' {} \;

                    if context.get('rm_dummy_class_invoke'):
                        rm_dummy_class_invoke(fname_path)

def fix_autoflake_remove_all_unused_imports(dir_path):
    fix_custom_lint(dir_path, {'fix_unused_import': True})

def main():
    #TODO: Use option "--" and "-"
    if len( sys.argv ) == 2 and os.path.isdir(sys.argv[1]):
        #fix_autoflake_remove_all_unused_imports(sys.argv[1])
        fix_custom_lint(sys.argv[1], context=None)
    elif len( sys.argv ) == 3 and os.path.isdir(sys.argv[1]):
        if sys.argv[2] == 'all':
            fix_custom_lint(sys.argv[1], context=None)
        elif sys.argv[2] == 'all_commit':
            for fix in ALL_FIXES:
                fix_custom_lint(sys.argv[1], context={fix: True})
                raw_input("[FIX] %s completed, please go to '%s' folder in other terminal"\
                        " and commit here and press any key to continue"%(fix, sys.argv[1]))
        else:
            fix_custom_lint(sys.argv[1], context={sys.argv[2]: True})
    else:
        #logging.warning("First param should be directoy path to check")
        print "First param should be directoy path to check"#ToDo: Add warning

if __name__ == '__main__':
    exit(main())
