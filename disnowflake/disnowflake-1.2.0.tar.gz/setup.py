import re
from setuptools import setup

version = ''

with open('disnowflake/__init__.py', mode='r', encoding='utf8') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')


if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass

readme = ''

with open('README.md', mode='r', encoding='utf8') as f:
    readme = f.read()

setup(
    name='disnowflake',
    version=version,
    packages=['disnowflake'],
    url='https://github.com/peco2282/disnowflake',
    license='MIT',
    author='peco2282',
    author_email='pecop2282@gmail.com',
    description='Discord snowflake changer',
    long_description=readme,
    python_requires='>=3.8.0'
)

