# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['videogrep']

package_data = \
{'': ['*'],
 'videogrep': ['model/*',
               'model/am/*',
               'model/conf/*',
               'model/graph/*',
               'model/graph/phones/*',
               'model/ivector/*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0', 'moviepy>=1.0.3,<2.0.0']

extras_require = \
{'full': ['vosk==0.3.32']}

entry_points = \
{'console_scripts': ['videogrep = videogrep.cli:main']}

setup_kwargs = {
    'name': 'videogrep',
    'version': '2.0.0',
    'description': 'Videogrep is a command line tool that searches through dialog in video files and makes supercuts based on what it finds. Like grep but for video.',
    'long_description': 'Videogrep\n=========\n\nVideogrep is a command line tool that searches through dialog in video files and makes supercuts based on what it finds. It will recognize `.srt` or `.vtt` subtitle tracks, or transcriptions that can be generated with vosk, pocketsphinx, and other tools.\n\n#### Examples\n\n* [The Meta Experience](https://www.youtube.com/watch?v=nGHbOckpifw)\n* [All the instances of the phrase "time" in the movie "In Time"](https://www.youtube.com/watch?v=PQMzOUeprlk)\n* [All the one to two second silences in "Total Recall"](https://www.youtube.com/watch?v=qEtEbXVbYJQ)\n* [A former press secretary telling us what he can tell us](https://www.youtube.com/watch?v=D7pymdCU5NQ)\n\n----\n\n## Installation\n\nVideogrep is compatible with Python versions 3.6 to 3.10.\n\n\n```\npip install videogrep\n```\n\nIf you want to transcribe videos, you also need to install [ffmpeg](http://ffmpeg.org/) and [vosk](https://alphacephei.com/vosk/).\n\nIf you\'re on a mac with homebrew you install ffmpeg with:\n\n```\nbrew install ffmpeg\n```\n\nTo install vosk:\n\n```\npip install videogrep[full]\n\n# or: pip install vosk\n```\n\nNote: the previous version of videogrep supported pocketsphinx for speech-to-text. Vosk seems *much* better so I\'ve added support for it and will likely be phasing out support for pocketsphinx.\n\n## Usage\n\nThe most basic use:\n\n```\nvideogrep --input path/to/video --search \'search phrase\'\n```\n\nYou can put any regular expression in the search phrase.\n\n**NOTE: videogrep requires a matching subtitle track with each video you want to use. The video file and subtitle file need to have the exact same name, up to the extension.** For example, `my_movie.mp4` and `my_movie.srt` will work, and `my_movie.mp4` and `my_movie_subtitle.srt` will *not* work.\n\nVideogrep will search for matching `srt` and `vtt` subtitles, as well as `json` transcript files that can be generated with the `--transcribe` argument.\n\n### Options\n\n#### `--input [filename(s)] / -i [filename(s)]`\n\nVideo or videos to use as input. Most video formats should work.\n\n\n#### `--output [filename] / -o [filename]`\n\nName of the file to generate. By default this is `supercut.mp4`. Any standard video extension will also work.\n\nVideogrep will also recognize the following extensions for saving files:\n  * `.mpv.edl`: generates an edl file playable by [mpv](https://mpv.io/) (useful for previews)\n  * `.m3u`: media playlist\n  * `.xml`: Final Cut Pro timeline, compatable with Adobe Premiere and Davinci Resolve\n\n```\nvideogrep --input path/to/video --search \'search phrase\' --output coolvid.mp4\n```\n\n\n#### `--search [query] / -s [query]`\n\nSearch term, as a regular expression.\n\n\n#### `--search-type [type] / -st [type]`\n\nType of search you want to perform. There are two options:\n\n* `sentence`: (default): Generates clips containing the full sentences of your search query.\n* `fragment`: Generates clips containing the exact word or phrase of your search query.\n\nBoth options take regular expressions. You may only use the `fragment` search if your transcript has word-level timestamps, which will be the case for youtube `.vtt` files, or if you generated a transcript using Videogrep itself.\n\n```\nvideogrep --input path/to/video --search \'experience\' --search-type fragment\n```\n\n#### `--max-clips [num] / -m [num]`\n\nMaximum number of clips to use for the supercut.\n\n\n#### `--demo / -d`\n\nShow the search results without making the supercut.\n\n\n#### `--randomize / -r`\n\nRandomize the order of the clips.\n\n\n#### `--padding [seconds] / -p [seconds]`\n\nPadding in seconds to add to the start and end of each clip.\n\n#### `--resyncsubs [seconds] / -rs [seconds]`\n\nTime in seconds to shift the shift the subtitles forwards or backwards.\n\n#### `--transcribe / -tr`\n\nTranscribe the video using [vosk](https://alphacephei.com/vosk/). This will generate a `.json` file in the same folder as the video. By default this uses vosk\'s small english model.\n\n**NOTE:** Because of some compatibility issues, vosk must be installed separately with `pip install vosk`.\n\n```\nvideogrep -i vid.mp4 --transcribe\n```\n\n#### `--model [modelpath] / -mo [modelpath]`\n\nIn combination with the `--transcribe` option, allows you to specify the path to a vosk model folder to use. Vosk models are [available here](https://alphacephei.com/vosk/models) in a variety of languages.\n\n```\nvideogrep -i vid.mp4 --transcribe --model path/to/model/\n```\n\n#### `--export-clips / -ec`\n\nExports clips as individual files rather than as a supercut.\n\n```\nvideogrep -i vid.mp4 --search \'whatever\' --export-clips\n```\n\n#### `--ngrams [num] / -n [num]`\n\nShows common words and phrases from the video.\n\n```\nvideogrep -i vid.mp4 --ngrams 1\n```\n\n\n----\n\n\n## Use it as a module\n\n```\nfrom videogrep import videogrep\n\nvideogrep(\'path/to/your/files\',\'output_file_name.mp4\', \'search_term\', \'search_type\')\n```\nThe videogrep module accepts the same parameters as the command line script. To see the usage check out the source.\n\n### Example Scripts\n\nAlso see the examples folder for:\n* [silence extraction](https://github.com/antiboredom/videogrep/blob/master/examples/only_silence.py)\n* [automatically creating supercuts](https://github.com/antiboredom/videogrep/blob/master/examples/auto_supercut.py)\n* [creating supercuts based on youtube searches](https://github.com/antiboredom/videogrep/blob/master/examples/auto_youtube.py)\n\n----\n\n',
    'author': 'Sam Lavigne',
    'author_email': 'splavigne@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://antiboredom.github.io/videogrep/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
