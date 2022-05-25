from setuptools import setup, find_packages

pkj_name = 'vuejs_translate'

with open('README.md') as f:
    readme = f.read()

setup(
    name='django-vuejs-translate',
    version='0.6.4',
    install_requires=[
        'django',
        'polib',
        'django-jinja',
        'jsmin'
    ],
    packages=[pkj_name] + [pkj_name + '.' + x for x in find_packages(pkj_name)],
    url='https://gitlab.com/cyberbudy/django-vuejs-translate',
    license='MIT',
    author='cyberbudy',
    author_email='cyberbudy@gmail.com',
    description='Generating translations from strings inside vuejs',
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ]

)
