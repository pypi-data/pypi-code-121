# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pbspark']

package_data = \
{'': ['*']}

install_requires = \
['protobuf>=3.20.0', 'pyspark>=3.2.0']

setup_kwargs = {
    'name': 'pbspark',
    'version': '0.5.0',
    'description': 'Convert between protobuf messages and pyspark dataframes',
    'long_description': '# pbspark\n\nThis package provides a way to convert protobuf messages into pyspark dataframes and vice versa using a pyspark udf.\n\n## Installation\n\nTo install:\n\n```bash\npip install pbspark\n```\n\n## Usage\n\nSuppose we have a pyspark DataFrame which contains a column `value` which has protobuf encoded messages of our `SimpleMessage`:\n\n```protobuf\nsyntax = "proto3";\n\npackage example;\n\nmessage SimpleMessage {\n  string name = 1;\n  int64 quantity = 2;\n  float measure = 3;\n}\n```\n\nUsing `pbspark` we can decode the messages into spark `StructType` and then flatten them.\n\n```python\nfrom pyspark.sql.session import SparkSession\nfrom pbspark import MessageConverter\nfrom example.example_pb2 import SimpleMessage\n\nspark = SparkSession.builder.getOrCreate()\n\nexample = SimpleMessage(name="hello", quantity=5, measure=12.3)\ndata = [{"value": example.SerializeToString()}]\ndf = spark.createDataFrame(data)\n\nmc = MessageConverter()\ndf_decoded = df.select(mc.from_protobuf(df.value, SimpleMessage).alias("value"))\ndf_flattened = df_decoded.select("value.*")\ndf_flattened.show()\n\n# +-----+--------+-------+\n# | name|quantity|measure|\n# +-----+--------+-------+\n# |hello|       5|   12.3|\n# +-----+--------+-------+\n\ndf_flattened.schema\n# StructType(List(StructField(name,StringType,true),StructField(quantity,IntegerType,true),StructField(measure,FloatType,true))\n```\n\nWe can also re-encode them into protobuf strings.\n\n```python\ndf_reencoded = df_decoded.select(mc.to_protobuf(df_decoded.value, SimpleMessage).alias("value"))\n```\n\nFor flattened data, we can also (re-)encode after collecting and packing into a struct:\n\n```python\nfrom pyspark.sql import Row\n\ndata = [Row(value=row).asDict(recursive=True) for row in df_flattened.collect()]\ndf_unflattened = spark.createDataFrame(\n    data=data,\n    schema=StructType(\n        [\n            StructField(\n                name="value",\n                dataType=mc.get_spark_schema(SimpleMessage),\n                nullable=True,\n            )\n        ]\n    ),\n)\ndf_unflattened.show()\ndf_reencoded = df_unflattened.select(\n    mc.to_protobuf(df_unflattened.value, SimpleMessage).alias("value")\n)\n```\n\nInternally, `pbspark` uses protobuf\'s `MessageToDict`, which deserializes everything into JSON compatible objects by default. The exceptions are\n* protobuf\'s bytes type, which `MessageToDict` would decode to a base64-encoded string; `pbspark` will decode any bytes fields directly to a spark `BinaryType`.\n* protobuf\'s well known type, Timestamp type, which `MessageToDict` would decode to a string; `pbspark` will decode any Timestamp messages directly to a spark `TimestampType` (via python datetime objects).\n\nCustom serde is also supported. Suppose we use our `NestedMessage` from the repository\'s example and we want to serialize the key and value together into a single string.\n\n```protobuf\nmessage NestedMessage {\n  string key = 1;\n  string value = 2;\n}\n```\n\nWe can create and register a custom serializer with the `MessageConverter`.\n\n```python\nfrom pbspark import MessageConverter\nfrom example.example_pb2 import ExampleMessage\nfrom example.example_pb2 import NestedMessage\nfrom pyspark.sql.types import StringType\n\nmc = MessageConverter()\n\n# register a custom serializer\n# this will serialize the NestedMessages into a string rather than a\n# struct with `key` and `value` fields\nencode_nested = lambda message:  message.key + ":" + message.value\n\nmc.register_serializer(NestedMessage, encode_nested, StringType)\n\n# ...\n\nfrom pyspark.sql.session import SparkSession\nfrom pyspark import SparkContext\nfrom pyspark.serializers import CloudPickleSerializer\n\nsc = SparkContext(serializer=CloudPickleSerializer())\nspark = SparkSession(sc).builder.getOrCreate()\n\nmessage = ExampleMessage(nested=NestedMessage(key="hello", value="world"))\ndata = [{"value": message.SerializeToString()}]\ndf = spark.createDataFrame(data)\n\ndf_decoded = df.select(mc.from_protobuf(df.value, ExampleMessage).alias("value"))\n# rather than a struct the value of `nested` is a string\ndf_decoded.select("value.nested").show()\n\n# +-----------+\n# |     nested|\n# +-----------+\n# |hello:world|\n# +-----------+\n```\n\nMore generally, custom serde functions should be written in the following format.\n\n```python\n# Encoding takes a message instance and returns the result\n# of the custom transformation.\ndef encode_nested(message: NestedMessage) -> str:\n    return message.key + ":" + message.value\n\n# Decoding takes the encoded value, a message instance, and path string\n# and populates the fields of the message instance. It returns `None`.\n# The path str is used in the protobuf parser to log parse error info.\n# Note that the first argument type should match the return type of the\n# encoder if using both.\ndef decode_nested(s: str, message: NestedMessage, path: str):\n    key, value = s.split(":")\n    message.key = key\n    message.value = value\n```\n',
    'author': 'flynn',
    'author_email': 'crf204@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/crflynn/pbspark',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
