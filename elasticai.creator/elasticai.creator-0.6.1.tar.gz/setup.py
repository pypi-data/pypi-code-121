# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['elasticai',
 'elasticai.creator',
 'elasticai.creator.brevitas',
 'elasticai.creator.brevitas.translation_functions',
 'elasticai.creator.examples',
 'elasticai.creator.examples.generate_vhdl_files',
 'elasticai.creator.integrationTests',
 'elasticai.creator.integrationTests.brevitas_representation',
 'elasticai.creator.integrationTests.vhdl',
 'elasticai.creator.mlframework',
 'elasticai.creator.precomputation',
 'elasticai.creator.qat',
 'elasticai.creator.systemTests',
 'elasticai.creator.systemTests.brevitas_representation',
 'elasticai.creator.tests',
 'elasticai.creator.tests.brevitas_representation',
 'elasticai.creator.tests.precomputation',
 'elasticai.creator.tests.qat',
 'elasticai.creator.tests.vhdl',
 'elasticai.creator.vhdl',
 'elasticai.creator.vhdl.precomputed_convs',
 'elasticai.creator.vhdl.templates',
 'elasticai.creator.vhdl.templates.precomputed_convs',
 'elasticai.creator.vhdl.vhdl_formatter']

package_data = \
{'': ['*']}

install_requires = \
['MonkeyType>=21.5.0,<22.0.0',
 'bitarray>=2.3.5,<3.0.0',
 'torch>=1.10.0,<2.0.0',
 'vsg>=3.9.0,<4.0.0']

extras_require = \
{'brevitas': ['brevitas>=0.7.0,<0.8.0',
              'onnx>=1.10.2,<2.0.0',
              'onnxoptimizer>=0.2.6,<0.3.0'],
 'examples': ['torchvision>=0.11.2,<0.12.0'],
 'systemtests': ['torchvision>=0.11.2,<0.12.0']}

setup_kwargs = {
    'name': 'elasticai.creator',
    'version': '0.6.1',
    'description': 'Design, train and compile neural networks optimized specifically for FPGAs.',
    'long_description': '# ElasticAi.creator\n\nDesign, train and compile neural networks optimized specifically for FPGAs.\nObtaining a final model is typically a three stage process.\n* design and train it using the layers provided in the `elasticai.creator` package.\n* translate the model to a target representation, e.g. VHDL\n* compile the intermediate representation with a third party tool, e.g. Xilinx Vivado (TM)\n\nThis version currently only supports [Brevitas](https://github.com/Xilinx/brevitas) and parts of VHDL as target representations.\n\nThe project is part of the elastic ai ecosystem developed by the Embedded Systems Department of the University Duisburg-Essen. For more details checkout the slides at [researchgate](https://www.researchgate.net/publication/356372207_In-Situ_Artificial_Intelligence_for_Self-_Devices_The_Elastic_AI_Ecosystem_Tutorial).\n\n\n## Table of contents\n\n- [Users Guide](#users-guide)\n  - [Install](#install)\n- [Developers Guide](#developers-guide)\n  - [Install Dev Dependencies](#install-dev-dependencies)\n\n\n## Users Guide\n\n#### Install\nYou can install the ElasticAI.creator as a dependency using pip:\n```bash\npython3 -m pip install "elasticai.creator"\n```\n\n\n## Structure of the Project\n\nThe structure of the project is as follows.\nThe [creator](elasticai/creator) folder includes all main concepts of our project, especially the qtorch implementation which is our implementation of quantized PyTorch layer.\nIt also includes the supported target representations, like the subfolder [brevitas](elasticai/creator/brevitas) is for the translation to Brevitas or the subfolder [vhdl](elasticai/creator/vhdl) for the translation to Vhdl.\nAdditionally, we have folders for [unit tests](elasticai/creator/tests), [integration tests](elasticai/creator/integrationTests) and [system tests](elasticai/creator/systemTests).\n\n\n## General Limitations\n\nBy now we only support Sequential models for our translations.\n\n## Developers Guide\n### Install Dev Dependencies\n- [poetry](https://python-poetry.org/)\n- recommended:\n  - [pre-commit](https://pre-commit.com/)\n  - [commitlint](https://github.com/conventional-changelog/commitlint) to help following our [conventional commit](https://www.conventionalcommits.org/en/v1.0.0-beta.2/#summary) guidelines\npoetry can be installed in the following way:\n```bash\npip install poetry\npip install pre-commit\npoetry install -D\npre-commit install\nnpm install --save-dev @commitlint/{config-conventional,cli}\nsudo apt install ghdl\n```\n\n### Commit Message Scopes\n\n- **qat**: quantization-aware-training\n  - Examples: `QConv1D`, `QLSTM`, autograd functions, etc.\n- **readme**\n- **precomputation**: entities that deal with the precomputation of ML components\n  - Examples: the `precomputable` decorator or the `IOTable` class\n- **vhdl**: vhdl code generation\n  - Examples: `vhdl.TruthTable`, `vhdl.LSTMCell`\n- **gh-workflow**\n- **pyproject**: changes to the `pyproject.toml` file will typically either update run or dev dependencies\n- **typing**: changing type annotations and changes to code to allow consistent type annotations\n- **pre-commit**\n\n### Adding new translation targets\nNew translation targets should be located in their own folder, e.g. Brevitas for translating from any language to Brevitas.\nWorkflow for adding a new translation:\n1. Obtain a structure, such as a list in a sequential case, which will describe the connection between every component.\n2. Identify and label relevant structures, in the base cases it can be simply separate layers.\n3. Map each structure to its function which will convert it, like for [example](elasticai/creator/brevitas/translation_mapping.py).\n4. Do such conversions.\n5. Recreate connections based on 1.\n\nEach sub-step should be separable and it helps for testing if common functions are wrapped around an adapter.\n\n### Syntax Checking\n\n[GHDL](https://ghdl.github.io/ghdl/) supports a [syntax checking](https://umarcor.github.io/ghdl/using/InvokingGHDL.html#check-syntax-s) which checks the syntax of a vhdl file without generating code.\nThe command is as follows:\n```\nghdl -s path/to/vhdl/file\n```\nSo, for example for checking the sigmoid source vhdl files in our project we can run:\n```\nghdl -s elasticai/creator/vhdl/source/sigmoid.vhd\n```\nFor checking all vhdl files together in our project we can just run:\n```\nghdl -s elasticai/creator/**/*.vhd\n```\n\n### Tests\n\nOur implementation is fully tested with unit, integration and system tests.\nPlease refer to the system tests as examples of how to use the Elastic Ai Creator Translator.\nYou can run one explicit test with the following statement:\n\n```python -m unittest discover -p "test_*.py" elasticai/creator/path/to/test.py```\n\nIf you want to run all tests, give the path to the tests:\n\n```python -m unittest discover -p "test_*.py" elasticai/creator/path/to/testfolder```\n\nYou can also run all tests together:\n\n```python -m unittest discover -p "test_*.py" elasticai/creator/translator/path/to/language/```\n\nIf you want to add more tests please refer to the Test Guidelines in the following.\n\n### Test style Guidelines\n\n#### File IO\nIn general try to avoid interaction with the filesystem. In most cases instead of writing to or reading from a file you can use a StringIO object or a StringReader.\nIf you absolutely have to create files, be sure to use pythons [tempfile](https://docs.python.org/3.9/library/tempfile.html) module and cleanup after the tests.\n\n\n#### Diectory structure and file names\nFiles containing tests for a python module should be located in a test directory for the sake of separation of concerns.\nEach file in the test directory should contain tests for one and only one class/function defined in the module.\nFiles containing tests should be named according to the rubric\n`test_ClassName.py`.\nNext, if needed for more specific tests define a class which is a subclass of unittest.TestCase like [test_brevitas_model_comparison](elasticai/creator/integrationTests/brevitas_representation/test_brevitas_model_comparison.py) in the integration tests folder.\nThen subclass it, in this class define a setUp method (and possibly tearDown) to create the global environment.\nIt avoids introducing the category of bugs associated with copying and pasting code for reuse.\nThis class should be named similarly to the file name.\nThere\'s a category of bugs that appear if  the initialization parameters defined at the top of the test file are directly used: some tests require the initialization parameters to be changed slightly.\nIts possible to define a parameter and have it change in memory as a result of a test.\nSubsequent tests will therefore throw errors.\nEach class contains methods that implement a test.\nThese methods are named according to the rubric\n`test_name_condition`\n\n#### Unit tests\nIn those tests each functionality of each function in the module is tested, it is the entry point  when adding new functions.\nIt assures that the function behaves correctly independently of others.\nEach test has to be fast, so use of heavier libraries is discouraged.\nThe input used is the minimal one needed to obtain a reproducible output.\nDependencies should be replaced with mocks as needed.\n\n#### Integration Tests\nHere the functions\' behaviour with other modules is tested.\nIn this repository each integration function is in the correspondent folder.\nThen the integration with a single class of the target, or the minimum amount of classes for a functionality, is tested in each separated file.\n\n#### System tests\nThose tests will use every component of the system, comprising multiple classes.\nThose tests include expected use cases and unexpected or stress tests.\n\n#### Adding new functionalities and tests required\nWhen adding new functions to an existing module, add unit tests in the correspondent file in the same order of the module, if a new module is created a new file should be created.\nWhen a bug is solved created the respective regression test to ensure that it will not return.\nProceed similarly with integration tests.\nCreating a new file if a functionality completely different from the others is created e.g. support for a new layer.\nSystem tests are added if support for a new library is added.\n\n#### Updating tests\nIf new functionalities are changed or removed the tests are expected to reflect that, generally the ordering is unit tests -> integration tests-> system tests.\nAlso, unit tests that change the dependencies should be checked, since this system is fairly small the internal dependencies are not always mocked.\n\nreferences: https://jrsmith3.github.io/python-testing-style-guidelines.html\n',
    'author': 'Department Embedded Systems - University Duisburg Essen',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/es-ude/elastic-ai.creator',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
