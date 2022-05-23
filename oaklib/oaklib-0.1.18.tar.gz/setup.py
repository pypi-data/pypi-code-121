# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['oaklib',
 'oaklib.conf',
 'oaklib.datamodels',
 'oaklib.implementations',
 'oaklib.implementations.aggregator',
 'oaklib.implementations.amigo',
 'oaklib.implementations.bioportal',
 'oaklib.implementations.fhir',
 'oaklib.implementations.kgx',
 'oaklib.implementations.neo4j',
 'oaklib.implementations.ols',
 'oaklib.implementations.ontobee',
 'oaklib.implementations.owlery',
 'oaklib.implementations.owlontology',
 'oaklib.implementations.pronto',
 'oaklib.implementations.robot',
 'oaklib.implementations.scigraph',
 'oaklib.implementations.skos',
 'oaklib.implementations.solor',
 'oaklib.implementations.solr',
 'oaklib.implementations.sparql',
 'oaklib.implementations.sqldb',
 'oaklib.implementations.tccm',
 'oaklib.implementations.ubergraph',
 'oaklib.implementations.umls',
 'oaklib.implementations.uniprot',
 'oaklib.implementations.wikidata',
 'oaklib.interfaces',
 'oaklib.io',
 'oaklib.omk',
 'oaklib.utilities',
 'oaklib.utilities.graph',
 'oaklib.utilities.lexical',
 'oaklib.utilities.mapping',
 'oaklib.utilities.reasoning',
 'oaklib.utilities.semsim',
 'oaklib.utilities.subsets',
 'oaklib.utilities.taxon']

package_data = \
{'': ['*']}

install_requires = \
['SPARQLWrapper',
 'SQLAlchemy>=1.4.32,<2.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'lark>=1.1.2,<2.0.0',
 'linkml-runtime>=1.1.9,<2.0.0',
 'networkx>=2.7.1,<3.0.0',
 'nxontology>=0.4.0,<0.5.0',
 'pronto>=2.4.5,<3.0.0',
 'ratelimit>=2.2.1,<3.0.0',
 'semsql>=0.1.3,<0.2.0',
 'sssom>=0.3.8,<0.4.0']

entry_points = \
{'console_scripts': ['omk = oaklib.omk.omk_cli:main',
                     'runoak = oaklib.cli:main']}

setup_kwargs = {
    'name': 'oaklib',
    'version': '0.1.18',
    'description': 'Ontology Access Kit: Python library for common ontology operations over a variety of backends',
    'long_description': '# Ontology Access Kit\n\nPython lib for common ontology operations over a variety of backends.\n\n[![PyPI version](https://badge.fury.io/py/oaklib.svg)](https://badge.fury.io/py/oaklib)\n![](https://github.com/incatools/ontology-access-kit/workflows/Build/badge.svg)\n[![badge](https://img.shields.io/badge/launch-binder-579ACA.svg)](https://mybinder.org/v2/gh/incatools/ontology-access-kit/main?filepath=notebooks)\n[![Downloads](https://pepy.tech/badge/oaklib/week)](https://pepy.tech/project/oaklib)\n[![DOI](https://zenodo.org/badge/6456239/linkml/linkml.svg)](https://zenodo.org/badge/latestdoi/6456239/linkml/linkml)\n\nThis library provides a collection of different [interfaces](https://incatools.github.io/ontology-access-kit/interfaces/index.html) for different kinds of ontology operations, including:\n\n - [lookup of basic features](https://incatools.github.io/ontology-access-kit/interfaces/basic.html) of an ontology element, such as it\'s label, definition, relationships, or aliases\n - search an ontology for a term\n - validating an ontology\n - updating, deleting, or modifying terms\n - ontology term matching\n - generating and visualizing subgraphs\n - provide specialized object models for more advanced operations, such as graph traversal, or OWL axiom processing, or text annotation\n\nThese interfaces are *separated* from any particular [backend](https://incatools.github.io/ontology-access-kit/implementations/index.html). This means the same API can be used regardless of whether the ontology:\n\n - is served by a remote API such as OLS or BioPortal\n - is present locally on the filesystem in owl, obo, obojson, or sqlite formats\n - is to be downloaded from a remote repository such as the OBO library\n - is queried from a remote database, including SPARQL endpoints (Ontobee/Ubergraph), A SQL database, a Solr/ES endpoint\n\n## Documentation:\n\n- [incatools.github.io/ontology-access-kit](https://incatools.github.io/ontology-access-kit)\n\n\n## Example\n\n```python\nresource = OntologyResource(slug=\'tests/input/go-nucleus.db\', local=True)\noi = SqlImplementation(resource)\nfor curie in oi.basic_search("cell"):\n    print(f\'{curie} ! {oi.get_label_by_curie(curie)}\')\n    for rel, fillers in oi.get_outgoing_relationships().items():\n        print(f\'  RELATION: {rel} ! {oi.get_label_by_curie(rel)}\')\n        for filler in fillers:\n            print(f\'     * {filler} ! {oi.get_label_by_curie(filler)}\')\n```\n\nFor more examples, see\n\n- [demo notebook](https://github.com/incatools/ontology-access-kit/blob/main/notebooks/basic-demo.ipynb)\n\n## Command Line\n\nDocumentation here is incomplete.\n\nSee [CLI docs](https://incatools.github.io/ontology-access-kit/cli.html)\n\n### Search\n\nUse the pronto backend to fetch and parse an ontology from the OBO library, then use the `search` command\n\n```bash\nrunoak -i obolibrary:pato.obo search osmol \n```\n\nReturns:\n\n```\nPATO:0001655 ! osmolarity\nPATO:0001656 ! decreased osmolarity\nPATO:0001657 ! increased osmolarity\nPATO:0002027 ! osmolality\nPATO:0002028 ! decreased osmolality\nPATO:0002029 ! increased osmolality\nPATO:0045034 ! normal osmolality\nPATO:0045035 ! normal osmolarity\n```\n\n### QC and Validation\n\nPerform validation on PR using sqlite/rdftab instance:\n\n```bash\nrunoak -i sqlite:../semantic-sql/db/pr.db validate\n```\n\n### List all terms\n\nList all terms obolibrary has for mondo\n\n```bash\nrunoak -i obolibrary:mondo.obo terms \n```\n\n### Lexical index\n\nMake a lexical index of all terms in Mondo:\n\n```bash\nrunoak  -i obolibrary:mondo.obo lexmatch -L mondo.index.yaml\n```\n\n### Search\n\nSearching over OBO using ontobee:\n\n```bash\nrunoak  -i ontobee: search tentacle\n```\n\nyields:\n\n```\nhttp://purl.obolibrary.org/obo/CEPH_0000256 ! tentacle\nhttp://purl.obolibrary.org/obo/CEPH_0000257 ! tentacle absence\nhttp://purl.obolibrary.org/obo/CEPH_0000258 ! tentacle pad\n...\n```\n\nSearching over a broader set of ontologies in bioportal (requires API KEY)\n\n```bash\nrunoak set-apikey bioportal YOUR-KEY-HERE\nrunoak  -i bioportal: search tentacle\n```\n\nyields:\n\n```\nBTO:0001357 ! tentacle\nhttp://purl.jp/bio/4/id/200906071014668510 ! tentacle\nCEPH:0000256 ! tentacle\nhttp://www.projecthalo.com/aura#Tentacle ! Tentacle\nCEPH:0000256 ! tentacle\n...\n```\n\nSearching over more limited set of ontologies in Ubergraph:\n\n```bash\nrunoak -v -i ubergraph: search tentacle\n```\n\nyields\n```\nUBERON:0013206 ! nasal tentacle\n```\n\n### Annotating Texts\n\n```bash\nrunoak  -i bioportal: annotate neuron from CA4 region of hippocampus of mouse\n```\n\nyields:\n\n```yaml\nobject_id: CL:0000540\nobject_label: neuron\nobject_source: https://data.bioontology.org/ontologies/NIFDYS\nmatch_type: PREF\nsubject_start: 1\nsubject_end: 6\nsubject_label: NEURON\n\nobject_id: http://www.co-ode.org/ontologies/galen#Neuron\nobject_label: Neuron\nobject_source: https://data.bioontology.org/ontologies/GALEN\nmatch_type: PREF\nsubject_start: 1\nsubject_end: 6\nsubject_label: NEURON\n\n...\n```\n\n### Mapping\n\nCreate a SSSOM mapping file for a set of ontologies:\n\n```bash\nrobot merge -I http://purl.obolibrary.org/obo/hp.owl -I http://purl.obolibrary.org/obo/mp.owl convert --check false -o hp-mp.obo\nrunoak lexmatch -i hp-mp.obo -o hp-mp.sssom.tsv\n```\n\n\n\n\n### Visualization of ancestor graphs\n\nUse the sqlite backend to visualize graph up from \'vacuole\' using test ontology sqlite:\n\n```bash\nrunoak -i sqlite:tests/input/go-nucleus.db  viz GO:0005773\n```\n\n![img](notebooks/output/vacuole.png)\n\nSame using ubergraph, restricting to is-a and part-of\n\n```bash\nrunoak -i ubergraph:  viz GO:0005773 -p i,BFO:0000050\n```\n\nSame using pronto, fetching ontology from obolibrary\n\n```bash\nrunoak -i obolibrary:go.obo  viz GO:0005773\n```\n\n## Documentation\n\n- [incatools.github.io/ontology-access-kit](https://incatools.github.io/ontology-access-kit)\n\n## Potential Refactoring\n\nCurrently all implementations exist in this repo/module, this results in a lot of dependencies\n\nOne possibility is to split out each implementation into its own repo and use a plugin architecture\n\n## PyPI release\n\nTODO\n',
    'author': 'cmungall',
    'author_email': 'cjm@berkeleybop.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
