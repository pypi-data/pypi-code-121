# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['vcfio', 'vcfio.utils', 'vcfio.variant']

package_data = \
{'': ['*']}

extras_require = \
{'bio': ['biopython>=1.79,<2.0', 'pysam>=0.18,<0.19']}

setup_kwargs = {
    'name': 'vcfio',
    'version': '1.0.0.dev0',
    'description': 'A simple and efficient VCF manipulation package.',
    'long_description': '<h1 align="center">\n  <br>\n  <img src="doc/logo.png" alt="vcfio" width="60%">\n  <br>\n\n\n</h1>\n\n# 🔭 Overview\nvcfio is an **efficient** and **easy-to-use** package for [VCF](https://samtools.github.io/hts-specs/VCFv4.2.pdf) reading, writing and manipluation.<br>\nIt is designed for robust variant processing, and requires *minimum* computing resources.\n\n- ⚡ Fast - iterate >4500 variants per second\n- 🪶 Lightweight - automatically parses only **crucial information** about variants (CHROM, POS, ID, REF, ALT, QUAL, FILTER), all the other information (INFO and SAMPLES) is parsed on demand\n- 🏁 Efficient - No advanced parsing of lines and casting to hugh memory objects\n- 🔌 Dependency free - We do have optional dependencies which enhance the package\n\n# 🎯 Why ? \nThe existing python VCF solutions were **extremely inefficient** - parsing every variant line in advance and casting \nevery bit of data into their own objects or a list of strings, which is very memory-consuming.\n\nThis affected our runtime by a huge factor.\n\n**We wrote vcfio to overcome those issues, making it a lightweight and dependency-free package.**\n\n\n# ⚙️ ️Installation\n```bash\n# Basic installation\npip install vcfio\n\n# Include optional dependencies\npip install vcfio[bio]\n```\n\n# ⭐ Features\n:heavy_check_mark: **Read and write** plain and compressed vcf (no specification needed) - `file.vcf`, `file.vcf.gz`, `file.vcf.bgz`.<br>\n:heavy_check_mark: **Automatically infer** the type of values in the file. For example `\'1,2,3\'` will yield `[1, 2, 3]`.<br>\n:heavy_check_mark: **Parse** values __*on demand*__ for maximum efficiency.<br>\n:heavy_check_mark: **Fetch** variant ranges within a chromosome.\n\n# ❓ How to Use\n### VcfReader\nHere are some examples of what you can do with VcfReader\n(We recommend you explore all the available methods)\n<details>\n    <summary>Click to view usage!</summary>\n    <img src="doc/vcfreader.gif">\n    <img src="doc/vcfreaderfetch.gif">\n</details>\n\n```python\nimport vcfio\n\nwith vcfio.VcfReader(\'/path/to/file.vcf\') as reader:\n    # Iterate variants\n    for variant in reader:  # type: vcfio.Variant\n        print(variant.to_vcf_line())\n        \n        # Iterate the variant\'s samples\n        for sample_name, sample in variant.samples.items():  # type: AnyStr, EasyDict\n            # Try to find "AD" in sample, if not found - find in variant\'s info, if the value is a dot - return None\n            ad = variant.get_value(\'AD\', sample_name, empty_value=\'.\')        \n            zygosity = variant.get_zygosity(sample_name)\n\n    # Fetch variants within the range chr3:1-1000\n    for variant in reader.fetch(\'chr3\', start=1, end=1000):  # type: vcfio.Variant\n        print(variant)\n```\n### VcfWriter\nHere is an example of what you can do with VcfWriter\n<details>\n    <summary>Click to view usage!</summary>\n    <img src="doc/vcfwriter.gif">\n</details>\n\n```python\nimport vcfio\n\n# This will open an existing vcf, introduce a new value to each variant\'s INFO and write to another vcf.gz\nwith vcfio.VcfReader(\'/path/to/output_file.vcf.gz\') as reader, \\\n        vcfio.VcfWriter(\'/path/to/output.vcf\', headers=reader.headers) as writer:  \n    for variant in reader:  # type: vcfio.Variant\n        variant.info[\'new_info_field\'] = \'new_info_value\'\n        writer.write_variant(variant)\n```\n\n### Variant\nHere are some examples of what you can do with Variant\n(We recommend you to explore all the available methods)\n<details>\n    <summary>Click to view usage!</summary>\n    <img src="doc/variant.gif">\n</details>\n\n```python\nimport vcfio\n\nvariant_line = "chr1\t726\t.\tG\tC,T\t500\t.\tDP=200;MQ=250.00\tGT:AD:AF:DP:GQ\t0/1:10,160,30:0.8,0.15:200:420"\n\n# This will parse the raw variant line into a Variant instance\nvariant = vcfio.Variant.from_variant_line(variant_line, sample_names=[\'proband\'])\nprint(\n    variant.quality,                        # --> 726\n    variant.chromosome,                     # --> "chr1"\n    variant.alt,                            # --> ["C", "T"]\n    variant.get_zygosity(\'proband\'),        # --> "HET"\n    variant.get_value(\'MQM\', \'proband\'),    # --> 250\n    variant.samples[\'proband\'].get(\'GT\')    # --> "0/1"\n)\n```\n\n### EasyDict\nA Dict-inherited class with a smart `get` method. It\'s main (and only) feature is to automatically infer the type of the value it returns.\nA vcf file rarely specifies the type of values within the variant\'s data so this object makes a bioinformaticaion\'s life easier and exempts him from casting-duty.\nIt is used in `vcfio.Variant`\'s attributes.\n```python\nd = EasyDict({\n\t\'simple_int\': 1,\n\t\'not_simple_int\': \'2\',\n\t\'this_is_not_a_list\': [\'abc\'],\n\t\'list_of_numbers\': [\'1\', 2, \'3.1\'],\n\t\'this_is_a_real_list\': [\'a\', \'b\', \'c\'],\n\t\'dot_is_not_a_value\': \'.\',\n    \'this_is_a_list\': \'1,2,3\',\n    \'this_is_a_list_but_i_like_strings\': \'1,2,3\'\n}) \nd.get(\'simple_int\')                                                 # --> 1\nd.get(\'not_simple_int\', infer_type=True)                            # --> 2\nd.get(\'this_is_not_a_list\', infer_type=True)                        # --> \'abc\'\nd.get(\'list_of_numbers\', infer_type=True)                           # --> [1, 2, 3.1]\nd.get(\'this_is_a_real_list\', infer_type=True)                       # --> [\'a\', \'b\', \'c\']\nd.get(\'dot_is_not_a_value\', empty_value=\'.\', infer_type=True)       # --> None\nd.get(\'this_is_a_list\', empty_value=\'.\', infer_type=True)           # --> [1, 2, 3]\nd.get(\'this_is_a_list_but_i_like_strings\', empty_value=\'.\')         # --> \'1,2,3\' \n```\n\n# Credits\nThis package uses the following open source packages:\n- [PyVCF](https://github.com/jdoughertyii/PyVCF/)\n',
    'author': 'shencar',
    'author_email': 'barak.shencar@gmail.com',
    'maintainer': 'shencar',
    'maintainer_email': 'barak.shencar@gmail.com',
    'url': 'https://github.com/emedgene/vcfio',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
