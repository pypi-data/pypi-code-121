from setuptools import setup

# version = "0.0.3"

setup(
    install_requires=[
        "django",
        "djangorestframework",
    ],
    # TODO: https://github.com/obytes/ob-dj-store/issues/3
    packages=[
        "ob_dj_store.apis",
        "ob_dj_store.core",
        "ob_dj_store.utils",
    ],
    tests_require=["pytest"],
    use_scm_version={
        "write_to": "version.py",
    },
    setup_requires=["setuptools_scm"],
)
