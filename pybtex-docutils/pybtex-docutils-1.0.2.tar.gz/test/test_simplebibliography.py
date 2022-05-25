import re
from docutils.core import publish_file
import docutils.parsers.rst.directives as directives

from pybtex_docutils import SimpleBibliography


def html_citation_ref(key):
    return re.compile(
        fr'<a class="citation-reference" '
        fr'href="#{key.lower()}" id="[a-zA-Z0-9_-]+" '
        fr'role="doc-biblioref">'
        fr'\[{key}]'
        fr'</a>')


def html_citation(key):
    return re.compile(
        fr'<div class="citation" id="{key.lower()}" role="doc-biblioentry">\s*'
        fr'<span class="label">'
        fr'<span class="fn-bracket">\[</span>'
        fr'(?:<a role="doc-backlink" href="#[a-zA-Z0-9_-]+">)?'
        fr'{key}'
        fr'(?:</a>)?'
        fr'<span class="fn-bracket">]</span>'
        fr'</span>')


def test_simplebibliography(test_roots):
    directives.register_directive("bibliography", SimpleBibliography)
    source_path = test_roots / "test_simplebibliography" / "index.rst"
    result = publish_file(source_path=str(source_path), writer_name="html5")
    assert re.search(html_citation_ref('Mandel2009'), result) is not None
    assert re.search(html_citation_ref('Evensen2003'), result) is not None
    assert re.search(html_citation_ref('Lorenc1986'), result) is None
    assert re.search(html_citation('Mandel2009'), result) is not None
    assert re.search(html_citation('Evensen2003'), result) is not None
    assert re.search(html_citation('Lorenc1986'), result) is not None
