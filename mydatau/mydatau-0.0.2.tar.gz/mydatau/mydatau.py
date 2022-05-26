from os                  import chdir, getcwd, name, rename, system, walk
from papermill           import execute_notebook
from rpy2.robjects       import r
from stata_kernel.config import config as stata_config
from oct2py              import Oct2Py

# autorun function
def autorun(path_data=getcwd(), *args, **kwargs):
    stata  = stata_config.get('stata_path')
    julia  = 'julia'                                   # must be in PATH
    octave = Oct2Py()

    chdir(path_data)                                   # cd to DATA/<folder>
    for root, dirs, files in walk('.'):
        for file in files:
            # 1. Jupyter
            if file.endswith('.ipynb'):
                execute_notebook(file, file, kwargs)
            # 2. R
            if file.endswith('.R'):
                with open(file + '.log', 'w') as f:
                    f.write(str(r.source(file)))
            # 3. Stata BE/SE/MP
            if file.endswith('.do'):
                system(stata + (' /' if name == 'nt' else ' -') + 'bq ' + file)
                rename(file.replace('.do', '.log'), file + '.log')
            # 4. Julia
            if file.endswith('.jl'):
                system(julia + ' ' + file + ' >' + file + '.log 2>&1')
            # 5. Octave/Matlab
            if file.endswith('.m'):
                with open(file + '.log', 'w') as f:
                    f.write(str(octave.eval(file.replace('.m', '()'))))
        break

if __name__ == '__main__':
    autorun()
