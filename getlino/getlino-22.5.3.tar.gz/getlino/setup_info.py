SETUP_INFO = dict(
    name='getlino',
    version='22.5.3',
    install_requires=['click', 'virtualenv', 'jinja2', 'distro', 'rstgen', 'GitPython'],
    # tests_require=['docker', 'atelier'],
    # test_suite='tests',
    description="A command-line tool for installing Lino in different environments.",
    long_description="""
``getlino`` is a command-line tool for installing Lino in different environments.

Note: If you **just want to install** Lino, then this documentation tree is
**not for you**. You want to read the `Hosting Guide
<https://hosting.lino-framework.org/>`__  or the `Developer Guide
<https://dev.lino-framework.org/>`__ instead. This documentation tree is for
people who want to help with developing the tool that you use to install Lino.

- Project homepage: https://gitlab.com/lino-framework/getlino
- Documentation:
  https://getlino.lino-framework.org/
  (mirrored at https://lino-framework.gitlab.io/getlino/)

    """,
    author='Rumma & Ko Ltd',
    author_email='info@lino-framework.org',
    url="https://gitlab.com/lino-framework/getlino",
    license_files=['COPYING'],
    entry_points={
        'console_scripts': ['getlino = getlino.cli:main']
    },

    classifiers="""\
Programming Language :: Python :: 3
Development Status :: 5 - Production/Stable
Environment :: Console
Framework :: Django
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: GNU Affero General Public License v3
Operating System :: OS Independent
Topic :: System :: Installation/Setup
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines())

SETUP_INFO.update(
    zip_safe=False,
    include_package_data=True)

SETUP_INFO.update(packages=[n for n in """
getlino
""".splitlines() if n])
