"""eBooks have a spec, but the metadata is all over the place.
The goal here is to normalize extracting that info and provide a generator to iterate over large collections.
"""


import logging
from pathlib import Path
from typing import Callable, Dict, Generator, List, Optional, Set, Tuple, Union

from ebooklib import epub
from ebooklib.epub import EpubBook, EpubException


def default_resolver(book: EpubBook, field: Optional[str]) -> Union[str, None]:
    """Handle the most common Dublin Core fields. The data is a series of tuples, where the first element is a value and
    the others are qualifiers. With no other info, we can extract the first value from the first tuple for a keyword in
    the Dublin Core fields
    """
    if field is not None:
        metadata = book.get_metadata('DC', field)
        if metadata:
            first_tuple = metadata[0]
            first_value = first_tuple[0]
            return first_value
    return None


def default_resolver_factory(field: str) -> Callable:
    """Make a mapping from one field to another if needed."""
    return lambda book: default_resolver(book, field)


def isbn_resolver(book: EpubBook) -> str:
    """Check all the known terrible ways isbns are stored in epubs and extract the most useful possible thing."""
    dc_field = 'identifier'
    known_schema_keys = [f"{{{epub.NAMESPACES['OPF']}}}scheme", 'id']
    known_fields = [
        'isbn',
        'ebookisbn',
        'eisbn',
    ]
    # sometimes we get a bare id of  'pub-identifier'
    metadata = book.get_metadata('DC', dc_field)
    found_value = None
    # we want isbn, so let's look for variants of it
    for (value, schema) in metadata:
        if schema_is_valid(schema, known_fields, known_schema_keys):
            found_value = value
            break
        if 'isbn:' in value:
            # sometimes we see a pub-identifier with a 'urn:isbn' format
            found_value = value.replace('isbn:', '').replace('urn:', '')
    # remove dashes for  [('978-0-307-48304-1', {'id': 'PrimaryID', '{http://www.idpf.org/2007/opf}scheme': 'ISBN'})]
    if found_value:
        found_value = found_value.replace('-', '')
    else:
        logging.debug(f"unable to find an isbn in {metadata=}")

    return found_value


def schema_is_valid(schema: Dict[str, str], known_fields: List[str], known_schema_keys: List[str]) -> bool:
    """Check every known schema key to see if one produces the known fields.
    If metadata is stored as a value and then multiple schemas that the value is good for, then we need to check each
    schema to see if it is valid for our purpose. Do we know a schema key (like '{http://www.idpf.org/2007/opf}scheme')
    that indicates it is the value for a field we are looking for (like 'isbn' or 'eisbn' etc)
    """
    # we will check every schema key
    for schema_key in known_schema_keys:
        schema_value = (schema.get(schema_key, '')).lower()
        if schema_value in known_fields:
            return True

        if any((known_field in schema_value for known_field in known_fields)):
            # sometimes we get isbn_1234567889
            return True
    return False


class EbookLister:
    """Given directories and fields, can produce a listing of all books, metadata fields and locations."""

    # resolvers = defaultdict(default_resolver_factory)
    # resolvers: Dict[str, Callable] = {'isbn', isbn_resolver}
    resolvers: Dict[str, Callable] = {}
    resolvers['isbn'] = isbn_resolver
    field_map = {'isbn': 'identifier', 'author': 'creator', 'uuid': 'identifier'}

    def __init__(self, directory_paths, metadata_fields):
        """Initialize the class.

        Args:
            directory_paths: a list of Paths or strings representing Paths.
            metadata_fields: the fields you want in the output tuple.
        """
        self.paths = self.create_paths(directory_paths)
        self.fields = metadata_fields
        self.supported_extensions = [
            '*.epub',
        ]

    @staticmethod
    def create_paths(directory_paths: List[Union[str, Path]]) -> Generator[Path, None, None]:
        """Given a list of Paths or strings representing paths, return a list of paths.

        Args:
            directory_paths: a list of Paths or strings representing Paths

        Returns:
            Generator[Path, None, None]: A generator of Paths
        """
        ret_paths = (Path(path) for path in directory_paths)
        return ret_paths

    def get_ebooks_generator(self) -> Generator[Dict, None, None]:
        """Lazily iterate over all ebook locations and their fields.

        Returns:
            A tuple of ebook locations and a dictionary of fields
        """
        field_tuples: List[Tuple[str, Optional[Callable]]] = [(field, None) for field in self.fields]
        for path in self.paths:
            for supported_extension in self.supported_extensions:
                for book_path in path.rglob(supported_extension):
                    # for each book, get the fields
                    yield self.get_ebook_fields(book_path, field_tuples)

    assert True

    @staticmethod
    def get_ebook_fields(ebook: Path, ebook_fields: List[Tuple[str, Union[Callable, None]]]) -> Dict:
        """get_ebook_fields.

        Args:
            ebook (Path): Path to an ebook
            ebook_fields (List[Tuple(str, Callable)]): a list of (field_name, normalization_rule)

        Returns:
            Dict: (location: list of fields)
        """
        resolved_fields: Dict[str, Union[Path, str, None]] = {'path': ebook}
        try:
            book = epub.read_epub(ebook)
            # if 'alinsky' in ebook.name:
            # import pudb

            # pu.db
            for (field, resolver) in ebook_fields:
                resolved_fields[field] = EbookLister.get_ebook_field(book, field, resolver)
        except (AttributeError, KeyError, EpubException) as e:
            logging.warning(f"Error reading from { ebook = }")
            logging.warning(e)
            resolved_fields.update({field: None for field, resolver in ebook_fields})
        return resolved_fields

    @staticmethod
    def get_ebook_field(book: EpubBook, field: str, resolver: Optional[Callable]) -> str | None:
        """get_ebook_fields.

        Args:
            book (EpubBook): A book to pull a field from
            field (str): Name of a field.
            resolver (Callable): function that takes (ebook, field) and returns resolved Data. None-> default_resolver

        Returns:
            str: resolved value of the field in the ebook
        """
        if resolver is None:
            mapped_field = EbookLister.field_map.get(field, field)
            resolver = EbookLister.resolvers.get(field, default_resolver_factory(mapped_field))
        # needed by mypy to know that we aren't trying to call() a None
        if resolver is not None:
            try:
                return resolver(book)
            except AttributeError as e:
                logging.warning(f"Error reading {field = } from { book = }")
                logging.warning(e)
                return None
        return None

    def get_ebooks_set(self, key_fields: List[str]) -> Set[Tuple[str, Dict]]:
        """Find a Set of ebooks where uniqueness is determined by the key_fields.

        Args:
            key_fields (List(str)): if these key_fields are already in the set new ebook paths will be skipped.

        Returns:
            Set(Tuple(str, Dict)): A Set of Paths to ebooks and their metadata
        """
        raise NotImplementedError
