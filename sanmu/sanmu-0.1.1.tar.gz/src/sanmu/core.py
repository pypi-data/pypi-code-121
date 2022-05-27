import pytest

from sanmu.runner._pytest.runner import MyPlugin


def main():
    return pytest.main(
        args=["--html=TestResults.html", "--self-contained-html"],
        plugins=[MyPlugin()],
    )
