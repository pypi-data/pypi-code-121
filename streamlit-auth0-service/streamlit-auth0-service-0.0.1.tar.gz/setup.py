# https://packaging.python.org/guides/packaging-namespace-packages/
import setuptools


def get_requirements(source):
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    required = []
    # do not add to required lines pointing to git repositories
    EGG_MARK = '#egg='
    for line in requirements:
        if line.startswith('-e git:') or line.startswith('-e git+') or \
                line.startswith('git:') or line.startswith('git+'):
            if EGG_MARK in line:
                package_name = line[line.find(EGG_MARK) + len(EGG_MARK):]
                required.append(f'{package_name} @ {line}')
            else:
                print('Dependency to a git repository should have the format:')
                print('git+ssh://git@github.com/xxxxx/xxxxxx#egg=package_name')
        else:
            required.append(line)

    return required


setuptools.setup(
    name="streamlit-auth0-service",
    version="0.0.1",
    author="Mohammad Yazdani",
    author_email="mohammad@atlasai.co",
    description="Service to authorize Streamlit page based on token in URL param.",
    # packages=setuptools.find_namespace_packages(include=['auth0.*']),
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=get_requirements('requirements.txt'),
)
