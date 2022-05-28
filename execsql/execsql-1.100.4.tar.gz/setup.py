import setuptools
import io

with io.open('README.md', encoding='utf-8') as f:
	long_description = f.read()

setuptools.setup(name='execsql',
	version='1.100.4',
	description="Runs a SQL script against a PostgreSQL, MS-Access, SQLite, MS-SQL-Server, MySQL, MariaDB, Firebird, or Oracle database, or an ODBC DSN.  Provides metacommands to import and export data, copy data between databases, conditionally execute SQL and metacommands, and dynamically alter SQL and metacommands with substitution variables.  Data can be exported in 18 different formats, including CSV, TSV, ODS, HTML, JSON, LaTeX, and Markdown tables, and using custom templates.",
	author='Dreas Nielsen',
	author_email='dreas.nielsen@gmail.com',
    url='https://osdn.net/project/execsql/',
	scripts=['execsql/execsql.py'],
    license='GPL',
	requires=[],
	python_requires = '>=2.7',
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'Environment :: Console',
		'Environment :: X11 Applications',
		'Environment :: Win32 (MS Windows)',
		'Intended Audience :: End Users/Desktop',
		'Intended Audience :: Information Technology',
		'Intended Audience :: System Administrators',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Natural Language :: English',
		'Operating System :: OS Independent',
		'Operating System :: POSIX',
		'Operating System :: Microsoft :: Windows',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 2.7',
		'Topic :: Database',
		'Topic :: Database :: Front-Ends',
		'Topic :: Office/Business',
		'Topic :: Scientific/Engineering'
		],
	keywords=['SQL', 'Postgres', 'PostgreSQL', 'SQLite', 'Firebird',
		'Access', 'SQL Server', 'MySQL', 'MariaDb', 'ODBC', 'Oracle', 'database',
		'xlrd', 'psycopg2', 'pyodbc', 'pymysql', 'fdb', 'cx_Oracle', 'cx-Oracle',
		'odfpy', 'ETL', 'CSV', 'TSV', 'XML', 'HTML', 'JSON', 'Feather', 'LaTeX', 'OpenDocument',
		'table', 'DBMS', 'Redshift', 'CockroachDB', 'query', 'script', 'import', 'export',
		'template', 'Jinja', 'Airspeed', 'zip'],
	long_description_content_type="text/markdown",
	long_description=long_description
	)
