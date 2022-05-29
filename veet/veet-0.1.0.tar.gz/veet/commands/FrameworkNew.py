from veet.commands import veet
from ..core.logging import Log
from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import os
import requests
import fnc


@veet.command(name="framework:new")
def handle(name: str, version: str = None):
    """
    Create a new Veet Framework project
    """
    try:
        if version is None:
            get_realeses = requests.get(
                "https://api.github.com/repos/veetuse/framework/releases").json()

            for release in get_realeses:
                get_realese = release
                break
        else:
            get_realese = requests.get(
                f"https://api.github.com/repos/veetuse/framework/releases/tags/v{version}").json()

        zipball_url = fnc.get("zipball_url", get_realese)
        version_tag = fnc.get("tag_name", get_realese)

        print(f'Creating application "{name}" version {version_tag}')

        with urlopen(zipball_url) as zip_response:
            with ZipFile(BytesIO(zip_response.read())) as zip_file:
                zip_file.extractall(os.getcwd())

        framework_directory = None

        for directory in os.listdir(os.getcwd()):
            if directory.startswith('veetuse-framework-'):
                framework_directory = directory
                break

        if framework_directory is not None:
            os.rename(f"{os.getcwd()}/{framework_directory}",
                      f"{os.getcwd()}/{name}")

        print(framework_directory, version_tag, zipball_url)
    except Exception as exception:
        Log.error(exception)