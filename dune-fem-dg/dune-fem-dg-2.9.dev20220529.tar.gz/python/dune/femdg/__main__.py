import subprocess
commands='''
mkdir femdg_tutorial
cd femdg_tutorial

TMPNAME=`mktemp -d -p ./`

# clone repo without history
git clone --depth 1 https://gitlab.dune-project.org/dune-fem/dune-fem-dg.git $TMPNAME
cd $TMPNAME

cp pydemo/camc-paper/*.py pydemo/camc-paper/*.hh pydemo/camc-paper/*.dgf ..
cd ..
rm -rf $TMPNAME
'''
subprocess.check_output(commands, shell=True)

print("###################################################################")
print("## The tutorial is now located in the 'femdg_tutorial' folder. ")
try:
    import matplotlib
except ImportError:
    print("## Note: some of the examples require the installation of 'matplotlib'.")
try:
    import scipy
except ImportError:
    print("## Note: some of the examples require the installation of 'scipy'.")
print("###################################################################")
