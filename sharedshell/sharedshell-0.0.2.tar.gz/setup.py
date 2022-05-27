import distutils.cmd
import os
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

class BenchmarkCommand(distutils.cmd.Command):
    """ A custom command to run benchmark. """

    description = 'run sharedshell benchmark'

    user_options = []

    def initialize_options(self):
        """ Override. """

        pass

    def finalize_options(self):
        """ Override. """

        pass

    def run(self):
        """ Run command. """

        self.announce('┌---------------------', level=distutils.log.INFO)
        self.announce('| os.system', level=distutils.log.INFO)
        self.announce('└--------------------', level=distutils.log.INFO)

        os.system('python3 -m pyperf command -v --quiet -w 0 -n 5 -l 1 -p 1 -- python3 benchmarks/benchmark_system.py')

        self.announce('┌---------------------', level=distutils.log.INFO)
        self.announce('| subprocess', level=distutils.log.INFO)
        self.announce('└---------------------', level=distutils.log.INFO)

        os.system('python3 -m pyperf command -v --quiet -w 0 -n 5 -l 1 -p 1 -- python3 benchmarks/benchmark_subproces.py')

        self.announce('┌---------------------', level=distutils.log.INFO)
        self.announce('| sharedshell', level=distutils.log.INFO)
        self.announce('└---------------------', level=distutils.log.INFO)

        os.system('python3 -m pyperf command -v --quiet -w 0 -n 5 -l 1 -p 1 -- python3 benchmarks/benchmark_sharedshell.py')

setup(
    test_suite='tests',
    packages=['sharedshell'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    cmdclass={
        'benchmark': BenchmarkCommand
    }
)
