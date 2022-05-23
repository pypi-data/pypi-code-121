from pathlib import Path

from src.settings import Settings
from tests import test_base

TEST_DIR = Path()


def setup_module(module):
    test_base.setup_module(module)


def setup_function(function):
    global TEST_DIR
    TEST_DIR = test_base.get_test_folder(function.__name__)
    TEST_DIR.mkdir(parents=True)


def test_from_file_creates_file_if_not_exists():
    assert not Path(TEST_DIR, "settings.json").exists()

    Settings.from_file(Path(TEST_DIR, "settings.json"))

    assert Path(TEST_DIR, "settings.json").exists()


def test_save_writes_to_same_file_as_loaded_from():
    settings_file_path = Path(TEST_DIR, "settings.json")
    # Create the settings file with content
    settings = Settings()
    settings.file_path = settings_file_path
    settings.save()

    # Load the settings file from the path
    settings = Settings.from_file(settings_file_path)

    # Update and save the settings object
    settings.pic_paths = [str(Path.cwd())]
    settings.save()

    # Load the settings file again and verify it has any non default values
    settings = Settings.from_file(settings_file_path)
    assert settings.pic_paths == [Path.cwd()]
