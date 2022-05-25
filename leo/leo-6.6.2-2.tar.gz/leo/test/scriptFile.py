#@+leo-ver=5-thin
#@+node:ekr.20210309083845.1: * script: check-files
"""
Issue https://github.com/leo-editor/leo-editor/issues/1789
"""
g.cls()
import glob

def munge(s):
    return s.replace('\\','/').lower()

ignore = [
    # Core...
    'format-code.py',       # Script.
    # External...
    'leoftsindex.py',       # User contributed.
    'sax2db.py',            # User contributed.
    'stringlist.py',        # User contributed.
    # Plugins...
    'baseNativeTree.py',    # No longer used. To be deleted?
    'leofts.py',            # User contributed.
    'qt_main.py',           # Created by Qt designer. Not used.
    'rst3.py',              # To be deleted?
]
ignore = [munge(z) for z in ignore]
# Find all paths for @<file> nodes.
seen = {}
for p in c.all_positions():
    if p.isAnyAtFileNode():
        path = munge(g.fullPath(c, p))
        seen [path] = path
# Check all .py files.  
for module in ('core', 'external', 'plugins'):
    print(f"checking {module}...")
    pat = g.os_path_finalize_join(g.app.loadDir, '..', module, '*.py')
    paths = glob.glob(pat)
    paths = [z for z in paths if not z.endswith('__init__.py')]
    paths = [munge(z) for z in paths]
    # g.printObj(paths, tag=f"\n{len(paths)} files in {module}")
    for path in paths:
        if path not in seen and g.shortFileName(path) not in ignore:
            print(f"Missing: {path}")
    print('')
print('done')
#@-leo

