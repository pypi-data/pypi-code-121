# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['gelatin_extract',
 'gelatin_extract.base',
 'gelatin_extract.io',
 'gelatin_extract.json',
 'gelatin_extract.json.schema',
 'gelatin_extract.xml',
 'gelatin_extract.xml.io',
 'gelatin_extract.xml.schema']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.8.0,<5.0.0', 'python-dateutil>=2.8.2,<3.0.0']

setup_kwargs = {
    'name': 'gelatin-extract',
    'version': '0.1.1',
    'description': 'lightweigh, simple, and fast declarative XML and JSON deserialization',
    'long_description': '# Gelatin Extract\n\nThis is kind of like Marshmallow, but only does deserialization. What it lacks in reversibility, it makes up for in speed. Schemas are compiled in advance allowing\ndeserialization to occur very quickly.\n\n## Motivation\n\nI have another package called patent_client. I also do a lot with legal data, some of which is in XML, and some of which is in JSON. But there\'s a lot of it. And I mean *a lot*, so speed matters.\n\n## Quick Start\n\nThere are two main modules: `sugar.json.schema` and `sugar.xml.schema`. Those modules support defining class-style deserializers. Both start by subclassing a `Schema` class, and then defining attributes from the `fields` submodule.\n\n### JSON Deserializer Example\n\n```python\n    from gelatin_extract.json.schema import Schema\n    from gelatin_extract.json.schema import fields\n\n    class JsonExample(Schema):\n        name = fields.String()\n        birthday = fields.Date("birthdate")\n        deep_data = fields.Int("something.0.many.levels.deep")\n\n    obj = {\n        "name": "Johnny Appleseed",\n        "birthdate": "2000-01-01",\n        "something": [\n            {"many": {\n                "levels": {\n                    "deep": 123\n                }\n            }}\n        ]\n    }\n\n    JsonExample().deserialize(obj)\n    # Returns\n    {\n        "name": "Johnny Appleseed",\n        "birthday": datetime.date(2000, 1, 1),\n        "deep_data": 123\n    }\n\n```\n\nFor JSON, the attributes are filled by pulling values off of the JSON object. If no\npath is provided, then the attribute name is used. Otherwise, a dotted string\ncan be used to pluck an item from the JSON object.\n\n### XML Deserializer Example\n\n```python\n    import lxml.etree as ET\n    from sugar.xml.schema import Schema\n    from sugar.xml.schema import fields\n\n    class XmlExample(Schema):\n        name = fields.String("./name")\n        birthday = fields.Date("./birthdate")\n        deep_data = fields.Int("./something/many/levels/deep")\n\n    obj = ET.fromstring(b"""\n    <xmlObject>\n        <name>Johnny Appleseed</name>\n        <birthdate>2000-01-01</birthdate>\n        <something>\n            <many>\n                <levels>\n                    <deep>123</deep>\n                </levels>\n            </many>\n        </something>\n    </xmlObject>\n    """.strip())\n\n    XmlExample().deserialize(obj)\n    # Returns\n    {\n        "name": "Johnny Appleseed",\n        "birthday": datetime.date(2000, 1, 1),\n        "deep_data": 123\n    }\n```\n\nFor XML, the attributes are filled using XPath expressions. If no path is provided,\nthen the entire object is passed to the field (no implicit paths). Any valid Xpath\nexpression can be used.\n\n',
    'author': 'Parker Hancock',
    'author_email': '633163+parkerhancock@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/parkerhancock/gelatin_extract',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
