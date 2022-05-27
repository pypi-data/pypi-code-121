# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['media_tools',
 'media_tools.util',
 'media_tools.util.buying',
 'media_tools.util.mixcloud']

package_data = \
{'': ['*']}

install_requires = \
['SoundFile>=0.10.3,<0.11.0',
 'audioread>=2.1.9',
 'coloredlogs>=15.0.1',
 'eyed3>=0.9.6,<0.10.0',
 'lxml>=4.8.0',
 'mutagen>=1.45.1',
 'pydub>=0.24.1',
 'pylast>=5.0.0',
 'python-magic>=0.4.25',
 'requests>=2.27.1',
 'tinytag>=1.8.1']

entry_points = \
{'console_scripts': ['backup_lastfm_data = '
                     'media_tools.backup_lastfm_data:entry',
                     'buy_most_played = media_tools.buy_most_played:main',
                     'clean_filenames = media_tools.clean_filenames:main',
                     'copy_from_playlist = media_tools.copy_from_playlist:main',
                     'mixcloud_upload = media_tools.mixcloud_upload:main',
                     'print_length = media_tools.print_length:main']}

setup_kwargs = {
    'name': 'media-tools',
    'version': '0.3.5',
    'description': 'Creating and managing playlists, and managing the filenames and directory structure for large numbers of music files.',
    'long_description': '-   [Installation](#installation)\n-   [Usage](#usage)\n    -   [`mixcloud_upload`](#mixcloud_upload)\n        -   [Authorization](#authorization)\n        -   [Configuration options](#configuration-options)\n    -   [`clean_filenames`](#clean_filenames)\n        -   [Checking results](#checking-results)\n    -   [Audacious playlist tools](#audacious-playlist-tools)\n        -   [`copy_from_playlist`](#copy_from_playlist)\n    -   [`buy_most_played`](#buy_most_played)\n    -   [`backup_lastfm_data`](#backup_lastfm_data)\n    -   [`print_length`](#print_length)\n-   [Development](#development)\n    -   [Test suite](#test-suite)\n    -   [Generating a Table of Contents to\n        `README.md`](#generating-a-table-of-contents-to-readme.md)\n\nToolbox for helping creating and managing playlists, and managing the filenames and directory\nstructure for large numbers of music files.\n\nThis is mostly tailored to my own usage patterns, although it may be useful to others.\n\nHome page: https://gitlab.com/lilacashes/music-library-tools\n\nPyPI page: https://pypi.org/project/media-tools\n\nInstallation\n============\n\n``` {.bash}\n$ pip install media-tools\n```\n\nUsage\n=====\n\n`mixcloud_upload`\n-----------------\n\nGenerate a mix on [Mixcloud](mixcloud.com) from the contents of a local directory.\n\nAssumes that the given directory contains a number of audio files as well as a picture file (JPEG or\nPNG format), one file called `description.txt` which contains the description which is printed along\nwith the mix on Mixcloud, and a file called `tags.txt` which contains a newline-separated list of\ntags for the mix. The mix is created as an audio file called `mix.mp3` in the given directory and\nthen uploaded to Mixcloud. The title of the mix on Mixcloud will be the name of the directory given,\nminus any leading numbers.\n\nExample: You have a directory structured like this:\n\n    10 - My awesome mix\n    |-- 01 - Awesome track.mp3\n    |-- 02 - Also awesome track.ogg\n    |-- 03 - Another pretty cool track.m4a\n    |-- 04 - This track rocks.flac\n    |-- cover.png\n    |-- description.txt\n    |-- tags.txt\n\n``` {.shell}\n$ mixcloud_upload -d "10 - My awesome mix"\n```\n\nwill upload this mix to Mixcloud under the name "My awesome mix" with track 01 to 04 in that order.\n\n### Authorization\n\nYou will need to generate an application on Mixcloud for your account and get an access token, as\ndescribed in the [Mixcloud API Documentation](https://www.mixcloud.com/developers/#authorization).\nStore this access token as `.mixcloud_access_token` in either the current directory, your user\'s\n`$HOME` directory or under `$HOME/.config/media-tools`.\n\n### Configuration options\n\n-   `-d DIRECTORY`, `--directory DIRECTORY`: Specify the folder containing the mix, as seen above\n-   `-e EXTENSIONS [EXTENSIONS ...]`, `--extensions EXTENSIONS [EXTENSIONS ...]`: List of file\n    extensions to consider as audio files for the mix. Per default, files ending in `.mp3`, `.MP3`,\n    `.flac`, `.m4a` and `.ogg` are treated as audio and added to the mix. Change this list of some\n    of your audio files have extensions that are not part of this list, or if you want to exclude\n    some of these extensions.\n-   `-q`, `--quiet`: Only errors are printed. Usually you want to omit `-q`, since the entire\n    generating and uploading process takes several minutes, so you want to be sure what is going on.\n-   `-s`, `--strict`: Do not upload the mix if any of these conditions are met:\n    -   There is no picture, no `descriptions.txt` or no `tags.txt` in the upload folder\n    -   Any of the audio tracks in the folder is missing the ID3 tag for title or artist. These tags\n        are needed to generate the tracklist for the mix.\n-   `-c CROSSFADE_MS`, `--crossfade-ms CROSSFADE_MS`: Number of milliseconds to use for crossfading\n    between two tracks. Currently, there can only be one global value which is used between all\n    tracks.\n-   `-r MAX_RETRY`, `--max-retry MAX_RETRY`: Maximum number of retries for failing uploads. Uploads\n    can fail for a number of reasons, such as rate limiting on the Mixcloud side, or because of a\n    bad internet connection. The default number of retries is set to 100, set this to a lower number\n    if you want to give up earlier.\n-   `-a`, `--auth-token-file`: explicitly specify the file containing the Mixcloud authorization\n    token.\n-   `-t`, `--auth-token-string`: explicitly specify the Mixcloud authorization token as a string.\n\n`clean_filenames`\n-----------------\n\nIn general: run a script with the `-v` option first to see what it would change. If satisfied, then\nre-run it with the `-f` option to effect those changes.\n\nRemoving useless duplicate strings from filenames:\n\n``` {.bash}\n$ clean_filenames -v clean-filenames --recurse .\n$ clean_filenames -f clean-filenames --recurse .\n```\n\nChanging filenames from different numbering schemes to the scheme `01 - filename.ext`:\n\n``` {.bash}\n$ clean_filenames -v clean-numbering .\n$ clean_filenames -f clean-numbering .\n```\n\nRemoving stray junk, such as underscores, stray dashes, and stray `[]` and `()` from filenames:\n\n``` {.bash}\n$ clean_filenames -v clean-junk .\n$ clean_filenames -f clean-junk .\n```\n\nUndoing renamings done with this script, limited to a specified directory and its subfolders, or a\nsingle file name:\n\n``` {.bash}\n$ clean_filenames -v undo .\n$ clean_filenames -f undo .\n# OR\n$ clean_filenames -f undo ./subdir/file_name.mp3\n```\n\nFixing symlinks to files which have been renamed by any of the previous commands:\n\n``` {.bash}\n$ clean_filenames -v fix-symlinks .\n$ clean_filenames -f fix-symlinks .\n```\n\n### Checking results\n\nFinding mp3 files which do not conform to the numbering scheme in general:\n\n``` {.bash}\n$ find . -name \\*.mp3 | grep -vE \'[[:digit:]]+ - .+\\.mp3\'\n```\n\nFinding mp3 files which have a number in their filename but do not conform to the numbering scheme,\nexcluding some more common use cases:\n\n``` {.bash}\n$ find . -name \\*.mp3 | \\\n    grep -E \'[[:digit:]]+[^/]+\\.mp3\' | \\\n    grep -vE \'[[:digit:]]+ - .+\\.mp3\' | \\\n    grep -vE \'[[:digit:]]{2}\\.mp3\'\n```\n\nAudacious playlist tools\n------------------------\n\nTools for making and repairing playlists containing physical music files from audacious playlists\nand the latest music files. The argument to `--playlist` defaults to the playlist currently playing\nin audacious.\n\n### `copy_from_playlist`\n\nCopying files from the current or specified playlist (as its name in the `playlists` subdir in the\naudacious configuration folder) to a specified target folder, optionally limiting the number of\nfiles to copy to the first NUM, and optionally renaming the files to reflect the position of the\nsong in the playlist:\n\n``` {.bash}\n$ copy_from_playlist [-v] copy \\\n    [--playlist PLAYLIST_ID] \\\n    [--number NUM] \\\n    [--renumber] \\\n    TARGET_DIR\n```\n\nTry to find files in the current playlist which are unavailable because they have been moved, and\nmove them back to the place in the filesystem which is noted on the playlist (does not appear to\nwork currently):\n\n``` {.bash}\n$ copy_from_playlist [-v] restore \\\n    [--playlist PLAYLIST_ID]\n```\n\nCopy the newest files to a specified target:\n\n``` {.bash}\n$ copy_from_playlist [-v] copy-newest \\\n    --max-age NUM_DAYS \\\n    --source SOURCE_DIR \\\n    --target TARGET_DIR\n```\n\n`buy_most_played`\n-----------------\n\nAttempt to buy your most played tracks (in a given period) from several platforms.\n\n...\n\n`backup_lastfm_data`\n--------------------\n\nBack up Last.FM scrobbles.\n\n...\n\n`print_length`\n--------------\n\nGiven a directory of audio files, print the total playing length of that directory and all\ndirectories below.\n\n...\n\nDevelopment\n===========\n\nAfter cloning, it is recommended to set up the git hook that runs the test suite before every\n`git push`:\n\n``` {.shell}\n$ cd .git/hooks\n$ ln -s ../../.git_hooks/pre-push .\n```\n\nTest suite\n----------\n\nRun all in one:\n\n``` {.shell}\n$ .git_hooks/pre-push\n```\n\nRun separately:\n\n``` {.shell}\n$ poetry run mypy .\n$ poetry run flake8 .\n$ poetry run pylint media_tools\n$ poetry run nosetests --with-coverage --cover-package=media_tools.util tests/unit\n$ poetry run nosetests tests/integration\n```\n\nGenerating a Table of Contents to `README.md`\n---------------------------------------------\n\n``` {.shell}\n$ git add README.md\n$ git commit -m \'Before ToC generation\'\n$ pandoc -s --columns 100 --toc --toc-depth=4 README.md -o README_toc.md\n$ mv README_toc.md README.md\n$ git add README.md\n$ git commit -m \'After ToC generation\'\n```\n',
    'author': 'Lene Preuss',
    'author_email': 'lene.preuss@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/lilacashes/music-library-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
