from setuptools import find_packages, setup

from bench import PROJECT_NAME, VERSION

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

with open("README.md") as f:
	long_description = f.read()

setup(
	name=PROJECT_NAME,
	description="Command line tools for Dodock/Dokos",
	long_description=long_description,
	long_description_content_type="text/markdown",
	version=VERSION,
	license="GPLv3",
	author="Dokos SAS / Frappe Technologies Pvt Ltd",
	author_email="hello@dokos.io",
	url="https://dokos.io",
	project_urls={
		"Documentation": "https://doc.dokos.io",
		"Source": "https://gitlab.com/dokos/docli",
	},
	classifiers=[
		"Development Status :: 5 - Production/Stable",
		"Environment :: Console",
		"License :: OSI Approved :: GNU Affero General Public License v3",
		"Natural Language :: English",
		"Operating System :: MacOS",
		"Operating System :: OS Independent",
		"Topic :: Software Development :: Build Tools",
		"Topic :: Software Development :: User Interfaces",
		"Topic :: System :: Installation/Setup",
	],
	packages=find_packages(),
	python_requires="~=3.6",
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
	entry_points={"console_scripts": ["bench=bench.cli:cli", "docli=bench.cli:cli"]},
)
