from setuptools import find_packages, setup
import os

def _post_install(setup):
    def _post_actions():
        home = os.path.expanduser('~')
        f = open('{}/cameron-says-hi'.format(home), 'w')
        f.write(':waves:')
        f.close()
    _post_actions()
    return setup

setup = _post_install(
    setup(
        name="dave-metrics",
        version="0.0.1",
        install_requires=["datadog==0.42.0"],
        extras_require={"test": ["pytest==6.2.2", "pytest-mock==3.5.1", "pytest-env"]},
        package_data={"dave-metrics": ["py.typed"]},
        packages=find_packages(include=["metrics", "metrics.**"]),
    )
)



