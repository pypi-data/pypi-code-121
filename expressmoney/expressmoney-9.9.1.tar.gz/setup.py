"""
py setup.py sdist
twine upload dist/expressmoney-9.9.1.tar.gz
"""
import setuptools

setuptools.setup(
    name='expressmoney',
    packages=setuptools.find_packages(),
    version='9.9.1',
    description='SDK ExpressMoney',
    author='Development team',
    author_email='dev@expressmoney.com',
    install_requires=('requests', 'google-cloud-error-reporting', 'google-cloud-tasks', 'google-cloud-secret-manager'),
    python_requires='>=3.7',
)
