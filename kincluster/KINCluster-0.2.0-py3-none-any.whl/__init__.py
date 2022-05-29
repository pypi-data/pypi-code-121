"""
KINCluster is clustering like KIN.

release note:
- version 0.2.0
    fix dependency errors(gensim)

- version 0.1.6
    fix settings
    update pipeline
    delete unused arguments
    fix convention by pylint
    now logging

- version 0.1.5.5
    fix using custom settings
    support both moudle and dict

- version 0.1.5.4
    Update tokenizer, remove stopwords eff

- version 0.1.5.3
    now custom setting available.
    see settings.py

- version 0.1.5.2
    change item, extractor, pipeline module
    now, pipeline.dress_item pass just item(extractor.dump)
    fix prev versions error (too many value to unpack)
"""

__version__ = '0.2.0'


from KINCluster.KINCluster import KINCluster

from KINCluster.core import (
    Cluster,
    Extractor,
    Item,
    Pipeline,
)

from KINCluster.lib import (
    tokenizer,
    stopwords,
)


__all__ = [
    'KINCluster',
    'Cluster',
    'Extractor',
    'Item',
    'Pipeline',
    'tokenizer',
    'stopwords',
]
