#!/usr/bin/env python
import os
import sys

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

def fix_autoflake_remove_all_unused_imports(dir_path):
    for dirname, dirnames, filenames in os.walk(dir_path):
            for filename in filenames:
                fname_woext, fext = os.path.splitext(filename)
                if fext == '.py' and fname_woext != '__init__' \
                    and fname_woext != '__openerp__'\
                    and fname_woext != '__terp__':
                    fname_path = os.path.join(dirname, filename)
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
                    with open(fname_path, "w") as fin:
                        fdata = fin.write( fdata )

def main():
    if len( sys.argv ) == 2 and os.path.isdir(sys.argv[1]):
        fix_autoflake_remove_all_unused_imports(sys.argv[1])
    else:
        logging.warning("First param should be directoy path to check")

if __name__ == '__main__':
    exit(main())