# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['viz_manga']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0',
 'requests>=2.27.1,<3.0.0',
 'viz-image-deobfuscate>=0.1.4,<0.2.0']

entry_points = \
{'console_scripts': ['viz-manga-cli = viz_manga.cli:main']}

setup_kwargs = {
    'name': 'viz-manga',
    'version': '0.1.4',
    'description': 'Viz Manga Reader',
    'long_description': '# Viz Manga Viewer\nRetrieves and deobfuscates manga pages for an input chapter id. Manga pages can be saves the dual spread images as well as single page images. Chapter ids need to be retrieved from the Viz site by looking at the chapter url.\n\nDISCLAIMER: I am not licensed or affiliated with Viz Media and this repository is meant for informational purposes only. Please delete the retrieved pages after reading.\n\n# Installation\n```\npip install viz_manga\n```\n\n# Usage\nThe `VizMangaDetails` class can be used to lookup series and chapter metadata and the `VizMangaFetch` class is used to actually get the chapter pages.\n\nTo get all the series that are publicly available:\n```\nfrom viz_manga import VizMangaDetails, VizMangaFetch\n\ndetails: VizMangaDetails = VizMangaDetails()\nseries: List[Series] = details.get_series()\n```\n\nTo get all the chapters that are publicly free for a series:\n```\nseries: Series = Series(None, "one-piece")\ndetails: VizMangaDetails = VizMangaDetails()\nfor chapter in details.get_series_chapters(series):\n    if chapter.is_free:\n        print(chapter)\n```\n\nTo get all pages for a chapter:\n```\nviz: VizMangaFetch = VizMangaFetch()\nviz.save_chapter(24297, "images/", combine=True):\n```\n\n# CLI Usage\nThis module is bundled with a CLI script `viz-manga-cli` that allows the user to lookup and get chapters without writing any code.\n\n```\nusage: viz-manga-cli [-h] {fetch,series,chapters} ...\n\nLookup Viz manga information.\n\npositional arguments:\n  {fetch,series,chapters}\n    fetch               Fetches and deobfuscates an entire manga chapter for reading.\n    series              Get series title and slug (for chapter lookup) obtained from the Viz site.\n    chapters            Get chapter title and id obtained from the Viz site.\n\noptions:\n  -h, --help            show this help message and exit\n\n```\n\n## Lookup Manga Series\n```\n>>> viz-manga-cli series\n\n{\'name\': \'7thGARDEN\', \'slug\': \'7th-garden\'}\n{\'name\': \'Agravity Boys\', \'slug\': \'agravity-boys\'}\n{\'name\': \'Akane-banashi\', \'slug\': \'akane-banashi\'}\n{\'name\': "Akira Toriyama\'s Manga Theater", \'slug\': \'akira-toriyamas-manga-theater\'}\n{\'name\': \'All You Need is Kill\', \'slug\': \'all-you-need-is-kill-manga\'}\n{\'name\': \'Assassination Classroom\', \'slug\': \'assassination-classroom\'}\n\n```\n\n## Lookup Manga Chapters\n```\n>>> viz-manga-cli chapters --help\nusage: viz-manga-cli chapters [-h] [--free] series_slug\n\npositional arguments:\n  series_slug  Series title for which to lookup chapter ids from the Viz site.\n\noptions:\n  -h, --help   show this help message and exit\n  --free       Only show publicly available free chapters for the series.\n\n>>> viz-manga-cli chapters 7th-garden\n\n{\'title\': \'ch-1\', \'id\': \'15220\', \'link\': \'https://www.viz.com/shonenjump/7th-garden-chapter-1/chapter/15220\', \'is_free\': True}\n{\'title\': \'ch-2\', \'id\': \'15221\', \'link\': \'https://www.viz.com/shonenjump/7th-garden-chapter-2/chapter/15221\', \'is_free\': True}\n{\'title\': \'ch-3\', \'id\': \'15222\', \'link\': \'https://www.viz.com/shonenjump/7th-garden-chapter-3/chapter/15222\', \'is_free\': True}\n{\'title\': \'ch-4\', \'id\': \'15223\', \'link\': \'https://www.viz.com/shonenjump/7th-garden-chapter-4/chapter/15223\', \'is_free\': False}\n{\'title\': \'ch-5\', \'id\': \'15224\', \'link\': \'https://www.viz.com/shonenjump/7th-garden-chapter-5/chapter/15224\', \'is_free\': False}\n\n```\n\n## Fetch Chapter\n```\n>>> viz-manga-cli fetch --help\nusage: viz-manga-cli fetch [-h] [--directory DIRECTORY] slug\n\npositional arguments:\n  slug                  Chapter id or series name obtained from the Viz site.\n\noptions:\n  -h, --help            show this help message and exit\n  --directory DIRECTORY\n                        Output directory to save the deobfuscated pages.\n\n>>> viz-manga-cli fetch 15220 --directory images/\n\nINFO:root:Getting 79 pages for Root 1: The Demon\'s Servant\nSuccessfully retrieved chapter 15220\n\n```\n\n## Fetch all free chapters from a series\nIMPORTANT: This is for reading purposes only, please delete after reading.\n\nIf a series slug is specified for `fetch`, it will try to retrieve all free chapters of the series, placing each chapter into it\'s own sub-directory. If a directory folder already exists for the chapter, the cli will skip that chapter.\n\n```\n>>> viz-manga-cli fetch one-piece --directory images/\n\nINFO:root:Getting 18 pages for One Piece Chapter 1049.0\nINFO:root:Successfully retrieved chapter ch-1049 at: images/ch-1049\nINFO:root:Getting 18 pages for One Piece Chapter 1048.0\nINFO:root:Successfully retrieved chapter ch-1048 at: images/ch-1048\nINFO:root:Getting 20 pages for One Piece Chapter 1047.0\nINFO:root:Successfully retrieved chapter ch-1047 at: images/ch-1047\nINFO:root:Successfully retrieved chapter ch-3 at: images/ch-3\nINFO:root:Getting 25 pages for Chapter 2: They Call Him “Straw Hat Luffy”\nINFO:root:Successfully retrieved chapter ch-2 at: images/ch-2\nINFO:root:Getting 55 pages for Chapter 1: Romance Dawn\nINFO:root:Successfully retrieved chapter ch-1 at: images/ch-1\n```\n\n# Docker\n```\n>>> docker build -t viz-manga .\n>>> docker run -v /home/user/images/:/app/images viz-manga fetch 24297 --directory images/\n\nINFO:root:Getting 20 pages for One Piece Chapter 1047.0\nSuccessfully retrieved chapter 24297\n\n```',
    'author': 'Kevin Ramdath',
    'author_email': 'krpent@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/minormending/viz-manga',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
