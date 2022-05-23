#!/usr/bin/env python
# coding: utf-8

import setuptools

setuptools.setup(
    name="mkdocs-github-wiki-edit-url",
    version='0.3',
    url='https://github.com/MichelZ/mkdocs-github-wiki-edit-url',
    author='Michel Zehnder',
    description='Use Edit URLs compatible with GitHub Wiki',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    entry_points={
        'mkdocs.plugins': [
            'github-wiki-edit-url=github_wiki_edit_url.plugin:GithubWikiEditUrlPlugin'
        ]
    }
)
