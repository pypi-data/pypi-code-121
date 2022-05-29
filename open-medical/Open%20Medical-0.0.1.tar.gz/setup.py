from setuptools import setup, find_packages
import codecs
import os

VERSION = '0.0.1'
DESCRIPTION = 'Given a query this project downloads articles from PubMed website and then do the following analysis: Summarization, Knowledge Grapg, NER, Topic Modeling'
# Setting up
setup(
    name="Open Medical",
    version=VERSION,
    author="Mehdi Hosseini Moghadam",
    author_email="<m.h.moghadam1996@gmail.com>",
    description=DESCRIPTION,
    packages=find_packages(),
    install_requires=['bert-extractive-summarizer',
    'bert-extractive-summarizer',
    'sacremoses',
    'pyvis',
    'awscli',
    'wikipedia-api',
    'neuralcoref',
    'transformers',
    'pymed',
    'pyLDAvis',],
    keywords=['PubMed', 'NLP', 'BioMedical', 'Biology', 'Summarization', 'BioMedical Summarization', 'Knowledge Graph', 'NER', 'Topic Modeling'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)