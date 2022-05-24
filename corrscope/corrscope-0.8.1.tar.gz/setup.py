# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['corrscope',
 'corrscope.generate',
 'corrscope.gui',
 'corrscope.settings',
 'corrscope.utils',
 'corrscope.utils.scipy']

package_data = \
{'': ['*']}

install_requires = \
['QtPy>=2.0.1,<3.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'appnope>=0.1.3,<0.2.0',
 'atomicwrites>=1.4.0,<2.0.0',
 'attrs>=21.2.0,<22.0.0',
 'click>=8.0.1,<9.0.0',
 'colorspacious>=1.1.2,<2.0.0',
 'matplotlib>=3.1,<4.0',
 'numpy>=1.21,<2.0',
 'ruamel.yaml>=0.17,<0.18']

extras_require = \
{'qt5': ['PyQt5>=5.15,<6.0'], 'qt6': ['PyQt6>=6.2,<7.0']}

entry_points = \
{'console_scripts': ['corr = corrscope.cli:main']}

setup_kwargs = {
    'name': 'corrscope',
    'version': '0.8.1',
    'description': 'Python program to render wave files into oscilloscope views, featuring advanced correlation-based triggering algorithm',
    'long_description': '# Corrscope\n\n[![Appveyor build status](https://ci.appveyor.com/api/projects/status/awiajnwd6a4uhu37/branch/master?svg=true)](https://ci.appveyor.com/project/nyanpasu64/corrscope/branch/master)\n[![Latest release](https://img.shields.io/github/v/release/corrscope/corrscope?include_prereleases)](https://github.com/corrscope/corrscope/releases)\n[![PyPI release](https://img.shields.io/pypi/v/corrscope.svg)](https://pypi.org/project/corrscope/)\n\nCorrscope renders oscilloscope views of WAV files recorded from chiptune (game music from retro sound chips).\n\nCorrscope uses "waveform correlation" to track complex waves (including SNES and Sega Genesis/FM synthesis) which jump around on other oscilloscope programs.\n\nSample results can be found on my Youtube channel at https://www.youtube.com/nyanpasu64/videos.\n\nDocumentation is available at https://corrscope.github.io/corrscope/.\n\n![Screenshot of Corrscope and video preview](docs/images/corrscope-screenshot.png?raw=true)\n\n## Status\n\nCorrscope is currently in semi-active development. The program basically works and I will fix bugs as they are discovered. Features will be added (and feature requests may be accepted) on a case-by-case basis. For technical support or feedback, contact me at Discord (https://discord.gg/CCJZCjc), or alternatively in the issue tracker (using the "Support/feedback" template). Pull requests may be accepted if they\'re clean.\n\n## Dependencies\n\n- FFmpeg\n\n## Installation\n\n### Installing Prebuilt Windows Binaries\n\nOn Windows, download Windows binary releases (.7z files) from the [Releases page](https://github.com/corrscope/corrscope/releases), then double-click `corrscope.exe` or run `corrscope (args)` via CLI.\n\n### Installing from PyPI via pipx (cross-platform, releases)\n\npipx creates an isolated environment for each program, and adds their binaries into PATH. I find this most reliable in practice, though it runs into issues after upgrading system Python in-place.\n\n- Install Python 3.8 or above.\n- Install pipx using either your Linux package manager, `pip3 install --user pipx`, or `pip install --user pipx`.\n- Run `pipx install corrscope[qt5]`\n    - On Linux, to add support for native Qt themes, instead run `pipx install --system-site-packages corrscope[qt5]`\n    - On M1 Mac, instead run `pipx install corrscope[qt6]`\n- Open a terminal and run `corr (args)`.\n\n### Installing from PyPI via Pip (cross-platform, releases)\n\npip installs packages into a per-user Python environment. This has the disadvantage that each program you install influences the packages seen by other programs. It might run into issues when upgrading system Python in-place; I haven\'t tested.\n\n- Install Python 3.8 or above.\n- If necessary, install pip using your Linux package manager.\n- Run `pip3 install --user corrscope[qt5]`\n    - On M1 Mac, instead run `pip3 install --user corrscope[qt6]`\n- Open a terminal and run `corr (args)`.\n\n### Dev builds (Windows)\n\nWindows dev builds are compiled automatically, and available at https://ci.appveyor.com/project/nyanpasu64/corrscope/history.\n\nInstalling dev builds on non-Windows platforms without cloning the repo (eg. Git URLs or .whl files) is not supported yet. Fixes are welcome.\n\n### Running from Source Code (cross-platform, dev master)\n\nInstall Python 3.8 or above, and Poetry. My preference is to run `pipx install poetry`. You can alternatively use the Poetry installer via `curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python`, but in the past, updating via `poetry self update` has broken and left me with no Poetry at all, requiring reinstalling.\n\n```shell\ncd path/to/corrscope\npoetry install -E qt5  # --develop is implied\n# On M1 Mac, instead run `poetry install -E qt6`.\npoetry run corr (args)\n```\n\n## GUI Tutorial\n\n1. Open GUI:\n    - `corrscope.exe` to create new project\n    - `corrscope.exe file.yaml` to open existing project\n1. Add audio to play back\n    - On the right side of the window, click "Browse" to pick a master audio file.\n1. Add oscilloscope channels\n    - On the right side of the window, click "Add" to add WAV files to be viewed.\n1. Edit settings\n    - Global settings on the left side of the window\n    - Per-channel on the right side\n1. Play or render to MP4/etc. video (requires ffmpeg)\n    - Via toolbar or menu\n\n## Command-line Tutorial\n\n1. Create YAML:\n    - `corrscope split*.wav --audio master.wav -w`\n    - Specify all channels on the command line.\n    - `-a` or `--audio` specifies master audio track.\n    - Creates file `master.yaml`.\n\n1. Edit `master.yaml` to change settings.\n\n1. Play (requires ffmpeg):\n    - `corrscope master.yaml -p/--play`\n\n1. Render and encode video (requires ffmpeg)\n    - `corrscope master.yaml -r/--render file.mp4` (other file extensions supported)\n\n## Mac-specific Issues\n\n### Preview audio cutting out\n\nWhen you preview a video in Corrscope, it sends video frames to ffplay, which opens a video player window and also plays synchronized audio. On Mac (at least my M1 MacBook Air running macOS 12.3), switching windows can cause ffplay to stutter and temporarily or semi-permanently stop playing audio (until you restart the preview). There is no fix for this issue at the moment.\n\nRendering does not stutter on M1, since neither corrscope nor ffmpeg are affected by app switching, or App Nap.\n\n### Gatekeeper\n\nOn Mac, if you render a video file, in some cases (eg. IINA video player) you may not be able to open the resulting files. Gatekeeper will print an error saying \'"filename.mp4" cannot be opened because it is from an unidentified developer.\'. If you see this message, try opening the file again. Once you silence the error once, it should not reappear.\n\n## Contributing\n\nIssues, feature requests, and pull requests are accepted.\n\nThis project uses [Black code formatting](https://github.com/ambv/black). Either pull request authors can reformat code before creating a PR, or maintainers can reformat code before merging.\n\nYou can install a Git pre-commit hook to apply Black formatting before each commit. Open a terminal/cmd in this repository and run:\n\n```sh\npip install --user pre-commit\npre-commit install\n```\n',
    'author': 'nyanpasu64',
    'author_email': 'nyanpasu64@tuta.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/corrscope/corrscope/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
