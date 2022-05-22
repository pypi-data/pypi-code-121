# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['web2preview', 'web2preview.tests']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.11.1,<5.0.0', 'requests>=2.27.1,<3.0.0']

entry_points = \
{'console_scripts': ['web2preview = web2preview.cli:main']}

setup_kwargs = {
    'name': 'web2preview',
    'version': '1.1.0',
    'description': 'Extracts OpenGraph, TwitterCard and Schema properties from a webpage.',
    'long_description': '# web2preview\n\nFor a given URL `web2preview` extracts its **title**, **description**, and **image url** using\n[Open Graph](http://ogp.me/), [Twitter Card](https://dev.twitter.com/cards/overview), or\n[Schema](http://schema.org/) meta tags, or, as an alternative, parses it as a generic webpage.\n\nThis is a **fork** of an excellent [webpreview] library and it maintains **complete and absolute**\ncompatibility with the original while fixing several bugs, enhancing parsing, and adding a new\nconvenient APIs.\n\n*Main differences between `web2preview` and `webpreview`*:\n\n* Enhanced parsing for generic web pages\n* No unnecessary `GET` request is ever made if `content` of the page is supplied\n* Complete fallback mechanism which continues to parse until all methods are exhausted\n* Python Typings are added across the entire library (**better syntax highlighting**)\n* New dict-like `WebPreview` result object makes it easier to read parsing results\n* Command-line utility to extract title, description, and image from URL\n\n## Installation\n\n```shell\npip install web2preview\n```\n\n## Usage\n\nUse the generic `web2preview` method to parse the page independent of its nature.\nIt tries to extract the values from Open Graph properties, then it falls back to\nTwitter Card format, then Schema. If none of them can extract all three of the title,\ndescription, and preview image, then webpage\'s content is parsed using a generic\nextractor.\n\n```python\n>>> from web2preview import web2preview\n\n>>> p = web2preview("https://en.wikipedia.org/wiki/Enrico_Fermi")\n>>> p.title\n\'Enrico Fermi - Wikipedia\'\n>>> p.description\n\'Italian-American physicist (1901–1954)\'\n>>> p.image\n\'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Enrico_Fermi_1943-49.jpg/1200px-Enrico_Fermi_1943-49.jpg\'\n\n# Access the parsed fields both as attributes and items\n>>> p["url"] == p.url\nTrue\n\n# Check if all three of the title, description, and image are in the parsing result\n>>> p.is_complete()\nTrue\n\n# Provide page content from somewhere else\n>>> content = """\n<html>\n    <head>\n        <title>The Dormouse\'s story</title>\n        <meta property="og:description" content="A Mad Tea-Party story" />\n    </head>\n    <body>\n        <p class="title"><b>The Dormouse\'s story</b></p>\n        <a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>\n    </body>\n</html>\n"""\n\n# This function call won\'t make any external calls,\n# only relying on the supplied content, unlike the example above\n>>> web2preview("aa.com", content=content)\nWebPreview(url="http://aa.com", title="The Dormouse\'s story", description="A Mad Tea-Party story")\n```\n\n### Using the command line\n\nWhen `web2preview` is installed via `pip` the accompanying command-line tool is intalled alongside.\n\n```shell\n$ web2preview https://en.wikipedia.org/wiki/Enrico_Fermi\ntitle: Enrico Fermi - Wikipedia\ndescription: Italian-American physicist (1901–1954)\nimage: https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Enrico_Fermi_1943-49.jpg/1200px-Enrico_Fermi_1943-49.jpg\n\n$ web2preview https://github.com/ --absolute-url\ntitle: GitHub: Where the world builds software\ndescription: GitHub is where over 83 million developers shape the future of software, together.\nimage: https://github.githubassets.com/images/modules/site/social-cards/github-social.png\n```\n\n*Note*: For the Original [webpreview] API please check the [official docs][webpreview].\n\n## Run with Docker\n\nThe docker image can be built and ran similarly to the command line.\nThe default entry point is the `web2preview` command-line function.\n\n```shell\n$ docker build -t web2preview .\n$ docker run -it --rm web2preview "https://en.m.wikipedia.org/wiki/Enrico_Fermi"\ntitle: Enrico Fermi - Wikipedia\ndescription: Enrico Fermi (Italian: [enˈriːko ˈfermi]; 29 September 1901 – 28 November 1954) was an Italian (later naturalized American) physicist and the creator of the world\'s first nuclear reactor, the Chicago Pile-1. He has been called the "architect of the nuclear age"[1] and the "architect of the atomic bomb".\nimage: https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Enrico_Fermi_1943-49.jpg/1200px-Enrico_Fermi_1943-49.jpg\n```\n\n*Note*: built docker image weighs around 210MB.\n\n[webpreview]: https://github.com/ludbek/webpreview',
    'author': 'vduseev',
    'author_email': 'vagiz@duseev.com',
    'maintainer': 'vduseev',
    'maintainer_email': 'vagiz@duseev.com',
    'url': 'https://github.com/vduseev/web2preview',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
