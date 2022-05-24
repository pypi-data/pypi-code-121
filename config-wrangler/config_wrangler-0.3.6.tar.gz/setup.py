# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['config_wrangler',
 'config_wrangler.config_data_loaders',
 'config_wrangler.config_templates',
 'config_wrangler.config_types']

package_data = \
{'': ['*']}

install_requires = \
['CaseInsensitiveDict>=1.0.0', 'StrEnum>=0.4.7,<0.5.0', 'pydantic>=1.8.2']

extras_require = \
{'pykeepass': ['pykeepass>=4.0.0'],
 'redshift': ['boto3>=1.21'],
 's3': ['boto3>=1.21'],
 'sqlalchemy': ['SQLAlchemy>=1.4']}

setup_kwargs = {
    'name': 'config-wrangler',
    'version': '0.3.6',
    'description': 'pydantic based configuration wrangler. Handles reading multiple ini or toml files with inheritance rules and variable expansions.',
    'long_description': '# Config Wrangler\n\n[![pypi](https://img.shields.io/pypi/v/config-wrangler.svg)](https://pypi.org/project/config-wrangler/)\n[![license](https://img.shields.io/github/license/arcann/config_wrangler.svg)](https://github.com/arcann/config_wrangler/blob/master/LICENSE)\n\npydantic based configuration wrangler. Handles reading multiple ini or toml files with inheritance rules and variable expansions.\n\n\n\n## Installation\n\nInstall using `pip install -U config-wrangler` or `conda install config-wrangler -c conda-forge`.\n\n## A Simple Example\n\nconfig.ini\n```ini\n[S3_Source]\nbucket_name=my.exmple-bucket\nkey_prefixes=processed/\nuser_id=AK123456789ABC\n# Not a secure way to store the password, but OK for local prototype or examples.\n# See KEYRING or KEEPASS for better options\npassword_source=CONFIG_FILE\nraw_password=My secret password\n\n[target_database]\ndialect=sqlite\ndatabase_name=${test_section:my_environment:source_data_dir}/example_db\n\n[test_section]\nmy_int=123\nmy_float=123.45\nmy_bool=Yes\nmy_str=ABC☕\nmy_bytes=ABCⓁⓄⓋ☕\nmy_list_auto_c=a,b,c\nmy_list_auto_nl=\n    a\n    b\n    c\nmy_list_auto_pipe=a|b|c\nmy_list_c=a,b,c\nmy_list_python=[\'x\',\'y\',\'z\']\nmy_list_json=["J","S","O","N"]\nmy_list_nl=\n    a\n    b\n    c\nmy_list_int_c=1,2,3\nmy_tuple_c=a,b,c\nmy_tuple_nl=\n    a\n    b\n    c\nmy_tuple_int_c=1,2,3\nmy_dict={1: "One", 2: "Two"}\nmy_dict_str_int={"one": 1, "two": 2}\nmy_set={\'A\',\'B\',\'C\'}\nmy_set_int=1,2,3\nmy_frozenset=A,B,C\nmy_date=2021-05-31\nmy_time=11:55:23\nmy_datetime=2021-05-31 11:23:53\nmy_url=https://localhost:6553/\n\n[test_section.my_environment]\nname=dev\n# For example to run we\'ll make both paths relative to current\ntemp_data_dir=.\\temp_data\\${test_section:my_environment:name}\nsource_data_dir=.\n```\n\npython code\n\n```py\nimport typing\nfrom datetime import date, time, datetime\n\nfrom pydantic import BaseModel, DirectoryPath, Field, AnyHttpUrl\n\nfrom config_wrangler.config_data_loaders.base_config_data_loader import BaseConfigDataLoader\nfrom config_wrangler.config_from_ini_env import ConfigFromIniEnv\nfrom config_wrangler.config_from_loaders import ConfigFromLoaders\nfrom config_wrangler.config_templates.config_hierarchy import ConfigHierarchy\nfrom config_wrangler.config_templates.s3_bucket import S3_Bucket\nfrom config_wrangler.config_templates.sqlalchemy_database import SQLAlchemyDatabase\nfrom config_wrangler.config_types.path_types import AutoCreateDirectoryPath\n\n\nclass S3_Bucket_KeyPrefixes(S3_Bucket):\n    key_prefixes: typing.List[str]\n\n\nclass Environment(ConfigHierarchy):\n    name: str = Field(..., env=\'env_name\')\n    temp_data_dir: AutoCreateDirectoryPath\n    source_data_dir: DirectoryPath\n\n\nclass TestSection(BaseModel):\n    my_int: int\n    my_float: float\n    my_bool: bool\n    my_str: str\n    my_bytes: bytes\n    my_list_auto_c: list\n    my_list_auto_nl: list\n    my_list_auto_pipe: list\n    my_list_python: list\n    my_list_json: list\n    my_list_c: list = Field(delimiter=\',\')\n    my_list_nl: list = Field(delimiter=\'\\n\')\n    my_list_int_c: typing.List[int] = Field(delimiter=\',\')\n    my_tuple_c: tuple = Field(delimiter=\',\')\n    my_tuple_nl: tuple = Field(delimiter=\'\\n\')\n    my_tuple_int_c: typing.Tuple[int, int, int] = Field(delimiter=\',\')\n    my_dict: dict\n    my_dict_str_int: typing.Dict[str, int]\n    my_set: set\n    my_set_int: typing.Set[int]\n    my_frozenset: frozenset\n    my_date: date\n    my_time: time\n    my_datetime: datetime\n    my_url: AnyHttpUrl\n    my_environment: Environment\n\n\nclass ETLConfig(ConfigFromIniEnv):\n    class Config:\n        validate_all = True\n        validate_assignment = True\n        allow_mutation = True\n\n    target_database: SQLAlchemyDatabase\n\n    s3_source: S3_Bucket_KeyPrefixes\n\n    test_section: TestSection\n\n\nclass ETLConfigAnyLoaders(ETLConfig):\n    def __init__(\n            self,\n            _config_data_loaders: typing.List[BaseConfigDataLoader],\n            **kwargs: typing.Dict[str, typing.Any]\n    ) -> None:\n        # Skip super and call the next higher class\n        ConfigFromLoaders.__init__(\n            self,\n            _config_data_loaders=_config_data_loaders,\n            **kwargs\n        )\n\n\ndef main():\n    config = ETLConfig(file_name=\'simple_example.ini\')\n\n    print(f"Temp data dir = {config.test_section.my_environment.temp_data_dir}")\n    # > Temp data dir = temp_data\\dev\n\n    print(f"Source data dir = {config.test_section.my_environment.source_data_dir}")\n    # > Source data dir = .\n\n    print(f"my_int = {config.test_section.my_int}")\n    # > my_int = 123\n\n    print(f"my_float = {config.test_section.my_float}")\n    # > my_float = 123.45\n\n    print(f"my_str = {config.test_section.my_str}")\n    # > my_str = ABC☕\n\n    print(f"my_list_auto_c = {config.test_section.my_list_auto_c}")\n    # > my_list_auto_c = [\'a\', \'b\', \'c\']\n\n    print(f"my_list_auto_nl = {config.test_section.my_list_auto_nl}")\n    # > my_list_auto_c = [\'a\', \'b\', \'c\']\n\n    print(f"my_dict = {config.test_section.my_dict}")\n    # > my_dict = {1: \'One\', 2: \'Two\'}\n\n    print(f"my_set = {config.test_section.my_set}")\n    # > my_set = {\'C\', \'A\', \'B\'}\n\n    print(f"my_time = {config.test_section.my_time}")\n    # > my_time = 11:55:23\n\n    print(f"my_datetime = {config.test_section.my_datetime}")\n    # > my_datetime = 2021-05-31 11:23:53\n\n    print(f"my_url = {config.test_section.my_url}")\n    # > my_url = https://localhost:6553/\n\n    # Getting DB engine (requires sqlalchemy optional install\n    engine = config.target_database.get_engine()\n    print(f"target_database.engine = {engine}")\n    # > target_database.engine = Engine(sqlite:///.example_db)\n\n    print("Getting S3 Data")\n    bucket = config.s3_source.get_bucket()\n    print(f"S3 bucket definition = {bucket}")\n    for prefix in config.s3_source.key_prefixes:\n        print(f"  bucket search prefix = {prefix}")\n    # > Getting S3 Data\n    # > credentials.py:56: UserWarning: Passwords stored directly in config or worse in code are not safe. Please make sure to fix this before deploying.\n    # > S3 bucket definitition = s3.Bucket(name=\'my.exmple-bucket\')\n    # > bucket search prefix = processed/\n\n\nif __name__ == \'__main__\':\n    main()\n\n```\n',
    'author': 'Derek Wood',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/arcann/config_wrangler',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
