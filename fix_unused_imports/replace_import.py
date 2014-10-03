#!/usr/bin/env python
import os
import sys
import ast
import subprocess

"""
@sys.argv[1]: path of dirname with all python packages.

This script delete remove all unused imports and remove all unused variable

This script required:
pip install autoflake
pip install pylint
sed

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
        'lineno': node.lineno,
        'col_offset': node.col_offset,
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


def fix_custom_lint(dir_path, context=None):
    if context is None:
        context = {
            'fix_unused_import': True,
            'fix_unused_var': True,
            'fix_autopep8': False,#By default False because is not complete
        }
    for dirname, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
              #if 'hr_expense_replenishment/' in dirname and filename == 'hr_expense.py':
              #if 'account_move_line_address' in dirname and filename == 'account_move_line.py':
              #if 'payroll_amount_residual' in dirname and filename == 'hr_payslip.py':
                fname_woext, fext = os.path.splitext(filename)
                fname_path = os.path.join(dirname, filename)
                if fext == '.py':
                    compile_ok_result = compile_ok(fname_path)
                    if not compile_ok_result:
                        print "*"*20,"syntaxis error in file",fname_path#TODO: Make a log warning
                        continue
                    if fname_woext not in ['__init__', '__openerp__', '__terp__']:
                        if context.get('fix_unused_var'):
                            run(["autoflake", "--remove-unused-variables", "-ri", fname_path])

                            cmd = ["pylint", "-d", "all", "-e", "W0104", "-r", "n", '--msg-template="{line}"', fname_path]
                            pylint_out = run_output(cmd)
                            linenos_to_delete = [int(s) for s in pylint_out.split() if s.isdigit()]
                            delete_linenos(fname_path, linenos_to_delete)

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
                            with open(fname_path) as fin:
                                fdata = fin.read()
                            #TODO: IMP with ast library
                            if "from openerp.osv import fields\nfrom openerp.osv import osv" in fdata:
                                fdata = fdata.replace("from openerp.osv import fields\nfrom openerp.osv import osv",
                                    "from openerp.osv import osv, fields")
                            if "from openerp.osv import osv\nfrom openerp.osv import fields" in fdata:
                                fdata = fdata.replace("from openerp.osv import osv\nfrom openerp.osv import fields",
                                    "from openerp.osv import osv, fields")
                            #TODO: Only re-save it if was modify
                            with open(fname_path, "w") as fin:
                                fdata = fin.write( fdata )

                        if context.get('fix_autopep8'):
                            open(fname_path + '.bkp', "w").write( open(fname_path, "r").read() )
                            run(["autopep8", "--max-line-length", "79", "-i", "--aggressive", "--aggressive", fname_path])
                            compile_ok_result = compile_ok(fname_path)
                            if compile_ok_result:
                                os.remove(fname_path + ".bkp")
                            else:
                                os.rename(fname_path + ".bkp", fname_path)


def fix_autoflake_remove_all_unused_imports(dir_path):
    fix_custom_lint(dir_path, {'fix_unused_import': True})

def main():
    #TODO: Use option "--" and "-"
    if len( sys.argv ) == 2 and os.path.isdir(sys.argv[1]):
        fix_autoflake_remove_all_unused_imports(sys.argv[1])
    elif len( sys.argv ) == 3 and os.path.isdir(sys.argv[1]):
        if sys.argv[2] == 'all':
            fix_custom_lint(sys.argv[1], context=None)
        else:
            fix_custom_lint(sys.argv[1], context={sys.argv[2]: True})
    else:
        logging.warning("First param should be directoy path to check")

if __name__ == '__main__':
    exit(main())
