#!/usr/bin/env python
"""Tests for `ebooks_lister` package."""

import tempfile
from pathlib import Path

import pytest
from ebooklib import epub

from ebooks_lister.ebooks_lister import EbookLister, default_resolver, schema_is_valid


def test_create_paths():
    """Take a bunch of paths and strings and return paths."""
    with tempfile.TemporaryDirectory() as td:
        paths = [f"{td}/foo", Path(f"{td}/bar"), "flagle"]
        new_paths = list(EbookLister.create_paths(paths))
        assert len(new_paths) == 3
        for np in new_paths:
            assert issubclass(type(np), Path)


def test_get_ebook_fields(sample_ebooks):
    """Prove we can get the fields we care about from ebooks, normalized."""
    fields = [('title', None), ('author', None), ('isbn', None)]
    # get the path to an ebook with metadata
    assert len(sample_ebooks) == 3
    # test when an ebook doesn't exist
    nonexistant = sample_ebooks[0]
    assert not Path(nonexistant).exists()
    # should throw an error when you try to get fields from nonexistant path
    with pytest.raises(OSError):
        details = EbookLister.get_ebook_fields(nonexistant, ['title', 'author', 'isbn'])
    # test when an ebook exists but doesn't have the metadata fields
    empty = sample_ebooks[1]
    assert Path(empty).exists()
    details = EbookLister.get_ebook_fields(empty, fields)
    assert details['path'] == empty
    for (field, resolver) in fields:
        assert details[field] is None


def test_get_ebook_fields_with_standard_identifiers(sample_standard_book):
    """Test with the Dublin Core identifiers."""
    assert Path(sample_standard_book).exists()
    details = EbookLister.get_ebook_fields(
        sample_standard_book, [('title', None), ('creator', None), ('identifier', None)]
    )
    assert details['title'] == 'Standard Book'
    assert details['creator'] == 'Author Ontherocks'
    assert details['identifier'] == 'id123456'


def test_get_ebook_fields_with_mapped_identifiers(sample_standard_book):
    """Test when the ebook has metadata in all of the alternates we know."""
    assert Path(sample_standard_book).exists()
    details = EbookLister.get_ebook_fields(sample_standard_book, [('title', None), ('author', None), ('isbn', None)])
    assert details['title'] == 'Standard Book'
    assert details['author'] == 'Author Ontherocks'
    assert details['isbn'] == 'id123456'


def test_schema_is_valid():
    """Test that we can parse and explore all the possible valid schemas."""
    schema = {'id': 'isbn'}
    known_fields = ['isbn', 'ebookisbn', 'eisbn']
    known_schema_keys = ['id']
    assert schema_is_valid(schema, known_fields, known_schema_keys)


def test_default_resolver():
    """Make sure default resolver works."""
    dummy_data = [('fafnir', 'the medium lobster'), ('brumble', 'qweegaw')]

    class Bumble:
        pass

    Bumble.get_metadata = lambda s, x, y: dummy_data if (x == 'DC' and y == 'Kevin') else 'horrible'
    bumble = Bumble()
    assert 'fafnir' == default_resolver(bumble, 'Kevin')


def test_get_ebooks_generator(tmp_path, sample_real_ebooks):
    """Check that we can iterate over standard and empty books."""
    ebl = EbookLister([tmp_path], ['title', 'author', 'isbn'])
    fields_generator = ebl.get_ebooks_generator()
    for details in fields_generator:
        if 'standard' in details['path'].stem:
            assert details['title'] == 'Standard Book'
            assert details['author'] == 'Author Ontherocks'
            assert details['isbn'] == 'id123456'
        elif 'empty' in details['path'].stem:
            assert details['title'] is None


def test_get_ebooks_generator_with_silly_field(tmp_path, sample_real_ebooks):
    """Check that we can iterate over standard and empty books, with empty field."""
    ebl = EbookLister([tmp_path], ['title', 'author', 'isbn', 'dribble'])
    fields_generator = ebl.get_ebooks_generator()
    for details in fields_generator:
        if 'standard' in details['path'].stem:
            assert details['title'] == 'Standard Book'
            assert details['author'] == 'Author Ontherocks'
            assert details['isbn'] == 'id123456'
            assert details['dribble'] is None
        elif 'empty' in details['path'].stem:
            assert details['title'] is None
            assert details['dribble'] is None


@pytest.fixture
def sample_standard_book(tmp_path):
    """Generate a standard ebook with our fave fields."""
    book = ebook_shell()
    # book.set_identifier('id123456')
    book.set_unique_metadata('DC', 'identifier', 'id123456', {f"{{{epub.NAMESPACES['OPF']}}}scheme": "ISBN"})
    book.set_title('Standard Book')
    book.add_author('Author Ontherocks')
    standard_book_path = tmp_path / "standard.epub"
    epub.write_epub(standard_book_path, book)
    return standard_book_path


def ebook_shell():
    """Populate all the standard items in an ebook."""
    book = epub.EpubBook()
    # gotta add these or our library breaks
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    return book


@pytest.fixture
def sample_empty_ebook(tmp_path):
    """Generate ebook without any metadata."""
    book = ebook_shell()
    empty_book_path = tmp_path / "empty.epub"
    epub.write_epub(empty_book_path, book)
    return empty_book_path


@pytest.fixture
def sample_real_ebooks(sample_standard_book, sample_empty_ebook):
    """Generate standard and empty test books."""
    return [sample_standard_book, sample_empty_ebook]


@pytest.fixture
def sample_ebooks(tmp_path, sample_standard_book, sample_empty_ebook):
    """Generate ebooks with test cases inside."""
    # get the path to an ebook with metadata
    # test when an ebook doesn't exist
    # test when an ebook exists but doesn't have the metadata fields
    # test when the ebook has metadata in all of the alternates we know
    ebooks = []
    # ebook that doesn't exist
    ebooks.append(tmp_path / "nonexistant.epub")
    ebooks.append(sample_empty_ebook)
    # an ebook with our fave fields
    ebooks.append(sample_standard_book)
    return ebooks
