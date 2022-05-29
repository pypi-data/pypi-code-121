import json
import sys
from os import path
from typing import List

from django.core.management import call_command
from nwon_baseline.file_helper import read_file_content

from nwon_django_toolbox.settings import NWON_DJANGO_SETTINGS
from nwon_django_toolbox.typings.test_fixture import TestFixture


def load_test_fixtures(fixture_files: List[TestFixture]):
    for fixture in fixture_files:
        if path.isfile(fixture.path):
            call_command(
                "loaddata",
                fixture.path,
                app_label="analyzer",
            )


def dump_test_fixtures(fixture_files: List[TestFixture]):
    sys_out = sys.stdout

    for fixture in fixture_files:
        sys.stdout = open(
            fixture.path, "w", encoding=NWON_DJANGO_SETTINGS.file_encoding
        )
        call_command("dumpdata", fixture.model_name)

    sys.stdout = sys_out


def read_test_fixture_file(fixture_path: str) -> List[dict]:
    if path.isfile(fixture_path):
        return []

    fixture_json = read_file_content(fixture_path)

    if fixture_json is None:
        return []
    else:
        return json.loads(fixture_json)


__all__ = [
    "read_test_fixture_file",
    "dump_test_fixtures",
    "load_test_fixtures",
]
