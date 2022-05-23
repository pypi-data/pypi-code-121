from flutter_gen.utils.loader import Loader
from ..config.config_cmd import ConfigCommand
from ..core.command import Command
from ..utils.utils import *
from ..utils.file_replace import replace
import requests
import shutil


class InstallCommand(Command):
    def __init__(self):
        super(InstallCommand, self).__init__()

    def run(self):
        loader = Loader("Loading...", 0.1).start()
        version_response = requests.get(
            "https://github.com/tien-px/pt_flutter_gen/raw/main/intellji/VERSION")
        version = version_response.text
        loader.stop()
        download_link = "https://github.com/tien-px/pt_flutter_gen/raw/main/intellji/flutter_architecture_plugin-%s.zip" % (
            version)
        folder = "/Users/it/Library/Application Support/Google/AndroidStudio2021.1/plugins"
        output_path = "%s/flutter_architecture_plugin.zip" % (folder)
        download_file(download_link, output_path)
        shutil.unpack_archive(output_path, folder)
        print("Successfully installed flutter_architecture_plugin-%s for Android Studio" % (version))
