# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pixelbin',
 'pixelbin.common',
 'pixelbin.platform',
 'pixelbin.platform.models',
 'pixelbin.utils']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'marshmallow>=3.15.0,<4.0.0',
 'pytz>=2022.1,<2023.0',
 'ujson>=5.2.0,<6.0.0']

setup_kwargs = {
    'name': 'pixelbin',
    'version': '1.0.2',
    'description': 'Pixelbin SDK for Python',
    'long_description': '# Pixelbin Backend SDK for Python\n\nPixelbin Backend SDK for python helps you integrate the core Pixelbin features with your application.\n\n## Getting Started\n\nGetting started with Pixelbin Backend SDK for Python\n\n### Installation\n\n```\npip install pixelbin\n```\n\n---\n\n### Usage\n\n#### Quick Example\n\n```python\nimport asyncio\n\nfrom pixelbin import PixelbinClient, PixelbinConfig\n\n# create client with your API_TOKEN\nconfig = PixelbinConfig({\n    "domain": "https://api.pixelbin.io",\n    "apiSecret": "API_TOKEN",\n})\n\n# Create a pixelbin instance\npixelbin:PixelbinClient = PixelbinClient(config=config)\n\n# Sync method call\ntry:\n    result = pixelbin.assets.listFiles()\n    print(result)\nexcept Exception as e:\n    print(e)\n\n# Async method call\ntry:\n    result = asyncio.get_event_loop().run_until_complete(pixelbin.assets.listFilesAsync())\n    print(result)\nexcept Exception as e:\n    print(e)\n```\n\n## Utilities\n\nPixelbin provides url utilities to construct and deconstruct Pixelbin urls.\n\n### url_to_obj\n\nDeconstruct a pixelbin url\n\n| parameter            | description          | example                                                                                               |\n| -------------------- | -------------------- | ----------------------------------------------------------------------------------------------------- |\n| pixelbinUrl (string) | A valid pixelbin url | `https://cdn.pixelbin.io/v2/your-cloud-name/z-slug/t.resize(h:100,w:200)~t.flip()/path/to/image.jpeg` |\n\n**Returns**:\n\n| property                | description                            | example                    |\n| ----------------------- | -------------------------------------- | -------------------------- |\n| cloudName (string)      | The cloudname extracted from the url   | `your-cloud-name`          |\n| zone (string)           | 6 character zone slug                  | `z-slug`                   |\n| version (string)        | cdn api version                        | `v2`                       |\n| transformations (array) | Extracted transformations from the url |                            |\n| filePath                | Path to the file on Pixelbin storage   | `/path/to/image.jpeg`      |\n| baseUrl (string)        | Base url                               | `https://cdn.pixelbin.io/` |\n\nExample:\n\n```python\nfrom pixelbin.utils.url import url_to_obj\n\npixelbinUrl = "https://cdn.pixelbin.io/v2/your-cloud-name/z-slug/t.resize(h:100,w:200)~t.flip()/path/to/image.jpeg"\nobj = url_to_obj(pixelbinUrl)\n# obj\n# {\n#     "cloudName": "your-cloud-name",\n#     "zone": "z-slug",\n#     "version": "v2",\n#     "transformations": [\n#         {\n#             "plugin": "t",\n#             "name": "resize",\n#             "values": [\n#                 {\n#                     "key": "h",\n#                     "value": "100"\n#                 },\n#                 {\n#                     "key": "w",\n#                     "value": "200"\n#                 }\n#             ]\n#         },\n#         {\n#             "plugin": "t",\n#             "name": "flip",\n#         }\n#     ],\n#     "filePath": "path/to/image.jpeg",\n#     "baseUrl": "https://cdn.pixelbin.io"\n# }\n```\n\n### obj_to_url\n\nConverts the extracted url obj to a Pixelbin url.\n\n| property                | description                            | example                    |\n| ----------------------- | -------------------------------------- | -------------------------- |\n| cloudName (string)      | The cloudname extracted from the url   | `your-cloud-name`          |\n| zone (string)           | 6 character zone slug                  | `z-slug`                   |\n| version (string)        | cdn api version                        | `v2`                       |\n| transformations (array) | Extracted transformations from the url |                            |\n| filePath                | Path to the file on Pixelbin storage   | `/path/to/image.jpeg`      |\n| baseUrl (string)        | Base url                               | `https://cdn.pixelbin.io/` |\n\n```python\nfrom pixelbin.utils.url import obj_to_url\n\nobj = {\n    cloudName: "your-cloud-name",\n    zone: "z-slug",\n    version: "v2",\n    transformations: [\n        {\n            plugin: "t",\n            name: "resize",\n            values: [\n                {\n                    key: "h",\n                    value: "100",\n                },\n                {\n                    key: "w",\n                    value: "200",\n                },\n            ],\n        },\n        {\n            plugin: "t",\n            name: "flip",\n        },\n    ],\n    filePath: "path/to/image.jpeg",\n    baseUrl: "https://cdn.pixelbin.io",\n}\nurl = obj_to_url(obj) # obj is as shown above\n# url\n# https://cdn.pixelbin.io/v2/your-cloud-name/z-slug/t.resize(h:100,w:200)~t.flip()/path/to/image.jpeg\n```\n\n## Documentation\n\n-   [API docs](documentation/platform/README.md)\n',
    'author': 'Pixelbin',
    'author_email': 'dev@pixelbin.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/pixelbin-dev/pixelbin-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
