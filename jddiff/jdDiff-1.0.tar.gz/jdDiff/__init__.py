from PyQt6.QtCore import QTranslator, QLocale
from PyQt6.QtWidgets import QApplication
from .MainWindow import MainWindow
from .Enviroment import Enviroment
import sys
import os


def main():
    app = QApplication(sys.argv)
    env = Enviroment()

    app.setApplicationName("jdDiff")
    app.setWindowIcon(env.icon)

    translator = QTranslator()
    language = env.settings.get("language")
    if language == "default":
        system_language = QLocale.system().name()
        translator.load(os.path.join(env.program_dir, "translations", "jdDiff_" + system_language.split("_")[0] + ".qm"))
        translator.load(os.path.join(env.program_dir, "translations", "jdDiff_" + system_language + ".qm"))
    else:
        translator.load(os.path.join(env.program_dir, "translations", "jdDiff_" + language + ".qm"))
    app.installTranslator(translator)

    w = MainWindow(env)
    w.show()

    sys.exit(app.exec())
