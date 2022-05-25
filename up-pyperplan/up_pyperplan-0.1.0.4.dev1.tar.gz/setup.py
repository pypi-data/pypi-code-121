#!/usr/bin/env python3

from setuptools import setup # type: ignore
import up_pyperplan


long_description=\
"""============================================================
    UP_PYPERPLAN
 ============================================================

    up_pyperplan is a small package that allows an exchange of
    equivalent data structures between unified_planning and Pyperplan.
"""

setup(name='up_pyperplan',
      version=up_pyperplan.__version__,
      description='up_pyperplan',
      author='AIPlan4EU Organization',
      author_email='aiplan4eu@fbk.eu',
      url='https://www.aiplan4eu-project.eu',
      packages=['up_pyperplan'],
      python_requires='>=3.7',
      install_requires=['pyperplan==2.1'],
      license='APACHE'
     )
