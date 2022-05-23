
import subprocess
from setuptools import setup, Extension

subprocess.call(['make', 'clean'])
subprocess.call(['make'])

memprocfs = Extension(
    'memprocfs.vmmpyc',
    sources = ['vmmpyc.c', 'oscompatibility.c', 'vmmpyc_kernel.c', 'vmmpyc_maps.c', 'vmmpyc_module.c', 'vmmpyc_modulemaps.c', 'vmmpyc_pdb.c', 'vmmpyc_process.c', 'vmmpyc_processmaps.c', 'vmmpyc_reghive.c', 'vmmpyc_regkey.c', 'vmmpyc_regmemory.c', 'vmmpyc_regvalue.c', 'vmmpyc_util.c', 'vmmpyc_vfs.c', 'vmmpyc_vmm.c', 'vmmpyc_physicalmemory.c', 'vmmpyc_virtualmemory.c', 'vmmpyc_scattermemory.c'],
    libraries = [':vmm.so'],
    library_dirs = ['.'],
    define_macros = [("LINUX", "")],
    include_dirs = ["includes"],
    extra_compile_args=["-I.", "-L.", "-l:vmm.so", "-shared", "-fPIC", "-fvisibility=hidden", "-Wall", "-Wno-unused-variable", "-Wno-format-truncation"],
    extra_link_args=["-Wl,-rpath,$ORIGIN", "-g", "-ldl", "-shared"],
    py_limited_api=True
    )

setup(
    name='memprocfs',
    version='4.8.3', # VERSION_END
    description='MemProcFS for Python',
    long_description='MemProcFS for Python : native extension for windows memory analysis and forensics',
    url='https://github.com/ufrisk/MemProcFS',
    author='Ulf Frisk',
    author_email='pcileech@frizk.net',
    license='GNU Affero General Public License v3',
    platforms='manylinux1_x86_64',
    python_requires='>=3.6',
    install_requires=['leechcorepyc >=2.6.0'],
    classifiers=[
        "Programming Language :: C",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: POSIX :: Linux",
    ],
	packages=['memprocfs'],
	package_data={'memprocfs': ['vmm.so', 'info.db']},
    ext_modules = [memprocfs],
    )

