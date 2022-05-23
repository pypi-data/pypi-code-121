from dataclasses import dataclass, field
from logging import getLogger

from .tokens_api import TokenClient
from .variables import uri_formats, work_types


logger = getLogger(__name__)


@dataclass
class TranslatorClient(TokenClient):
    """Client for querying the translation service."""

    translator_api_base: str = field(default=None)
    translate_endpoint: str = field(default=None)
    works_endpoint: str = field(default=None)
    uris_endpoint: str = field(default=None)
    titles_endpoint: str = field(default=None)

    remove_uri_trailing_slash: bool = field(default=False)
    use_lower_case_uris: bool = field(default=True)
    enforce_canonical: bool = field(default=True)

    uri_formats = uri_formats
    work_types = work_types

    def __post_init__(self):
        if self.translator_api_base:

            api_base = self.translator_api_base.rstrip('/')

            if not self.translate_endpoint:
                self.translate_endpoint = f'{api_base}/translate'
            if not self.works_endpoint:
                self.works_endpoint = f'{api_base}/works'
            if not self.uris_endpoint:
                self.uris_endpoint = f'{api_base}/uris'
            if not self.titles_endpoint:
                self.titles_endpoint = f'{api_base}/titles'

        super().__post_init__()

    def show_work_types(self):  # helper function for reference
        print(
            f'Initial work types saved to the Translation Service Database:'
            f'\n\n{self.work_types}\n'
        )

    def show_uri_schemes(self):  # helper function for reference
        print(
            f'Prefixes to use for different uris, excludes http-like and '
            f'publisher-specific URIs:' 
            f'\n\n{self.uri_formats}\n'
        )

    @staticmethod
    def get_scheme_from_uri(uri):
        """Not guaranteed to work for DOIS."""
        return uri.rsplit(':', 1)[0]

    def format_uri(self, uri):
        """Convert URIs to lower case and removal of trailing slash."""
        if self.remove_uri_trailing_slash:
            uri = uri.rstrip('/')

        if self.use_lower_case_uris:
            uri = uri.lower()

        return uri

    def get_work_uris(self, work_uuid):
        """Fetch and all URIs associated with a given work.

        Args:
            work_uuid (str): UUID of work to search against.

        Returns:
            list: URIs registered with the work.
        """
        response = self.get(self.works_endpoint, params={'uuid': work_uuid})
        content = response.json()['data'][0]['URI']

        if response.status_code != 200:
            raise ValueError(response.content.decode('utf-8'))

        return [uri_entry.get('URI') for uri_entry in content]

    def work_exists(self, uri, uri_scheme):
        """Check if work exists, and return work uuid if it does.

        Args:
            uri (str): Main identifier for the work to search against.
            uri_scheme (str): URI scheme to normalise to.
        Returns:
            tuple: (bool, str) whether work exists and work UUID.
        """
        params = {
            'uri': self.format_uri(uri),
            'filter': f'uri_scheme:{uri_scheme}'
        }
        response = self.get(self.translate_endpoint, params=params)

        if response.status_code == 404:
            return False, []

        work_content = response.json()['data']
        uuids = set(uri_entry['work']['UUID'] for uri_entry in work_content)

        if len(uuids) > 1:
            raise ValueError(f'More than one work matching {uri}')

        try:
            work_uuid = uuids.pop()
        except KeyError:
            raise ValueError(f'Unexpected response from API: {response.json()}')

        return True, work_uuid

    def uri_to_id(self, uri, uri_scheme, uri_strict=False):
        """Query translator to convert a URI to specified schema.

        Args:
            uri (str): URI to query against.
            uri_scheme (str): URI scheme to normalise to.
            uri_strict (bool): Output errors with ambiguous translation queries.

        Returns:
            list: URIs matching the schema specified.
        """
        uri = self.format_uri(uri)
        uri_cache_key = f'{uri_scheme}-{uri_strict}'

        """Handle Multiple Canonical Identifiers linked to different works
        
        The translator service does not act as expected as far as this is 
        concerned - if `uri_strict` is set to True when querying the API, 
        it expects that only one work should match the identifier queried, 
        which does not suit our purposes
        
        We need to extract all unique canonical identifiers associated with 
        the URI queried (if `uri_strict=True` is specified) 
        """

        if self.ignore_cache or uri_cache_key not in self._cache.get(uri, {}):
            params = {'uri': uri, 'filter': f'uri_scheme:{uri_scheme}'}
            response = self.get(self.translate_endpoint, params=params)

            if response.status_code != 200:
                logger.warning(
                    f"[Response Code: {response.status_code}]: "
                    f"{response.json()['message']}: {uri}"
                )
                return []

            elif uri_strict and self.enforce_canonical:
                _canonical_uris, data = [], []
                # Not a fan of this logic, but I think it's necessary.
                for work in response.json()['data']:
                    if work['canonical'] and work['URI'] not in _canonical_uris:
                        _canonical_uris.append(work['URI'])
                        data.append(work)

                if not data:
                    raise ValueError(
                        f'Multiple Identifiers returned when fetching URIs '
                        f'for work {uri} and the scheme {uri_scheme}. This is '
                        f'not allowed when uri_strict is set to True. Either '
                        f'set this to False or make sure that the work has a '
                        f'canonical identifier set for the relevant work '
                        f'scheme.'
                    )
            else:
                data = response.json()['data']

            uri_cache = self._cache.setdefault(uri, {})
            uri_cache[uri_cache_key] = data

        identifiers = self._cache[uri][uri_cache_key]

        return identifiers

    def prepare_uri(self, uri, uri_type):
        """Convert URI to the format used by the translator.

        Args:
            uri (str): The value of the identifier
            uri_type (str): What type of identifier it is - doi, isbn, etc.

        Returns:
            str: URI in the format required by the translator.
        """
        uri_prefix = self.uri_formats[uri_type]
        uri = self.format_uri(uri.strip())

        return f'{uri_prefix}:{uri}'

    def get_all_books(self):
        """Fetch all books stored in the translator."""

        filters = (
            'work_type:monograph,work_type:book,uri_scheme:info:doi,'
            'uri_scheme:urn:isbn,uri_scheme:http,uri_scheme:https'
        )
        response = self.get(self.works_endpoint, params={'filter': filters})

        if response.status_code != 200:
            raise ValueError(response.content.decode('utf-8'))

        return response.json()['data']

    def post_new_uri(self, work_uuid, uri, canonical=False):
        """Post a new URI for a work.

        Args:
            work_uuid (str): UUID of work in the translator database.
            uri (str): new URI to send.
            canonical (bool): Set True if the uri is the canonical identifier.
        """
        data = {
            'UUID': work_uuid,
            'URI': self.format_uri(uri),
            'canonical': canonical,
        }
        response = self.post(self.uris_endpoint, json=data)

        if response.status_code not in (200, 201):
            reason = response.content.decode('utf-8')
            logger.error(
                f'Failed to update work {work_uuid} with URI {uri}: {reason}'
            )

        return response

    def delete_uri(self, work_uuid, uri):
        """Delete a URI from a work.

        Args:
            work_uuid (str): UUID of work in the translator database.
            uri (str): new URI to send.
        """
        data = {
            'UUID': work_uuid,
            'URI': self.format_uri(uri)
        }
        response = self.delete(self.uris_endpoint, params=data)

        if response.status_code not in (200, 201):
            reason = response.content.decode('utf-8')
            logger.error(
                f'Failed to delete URI {uri} from work {work_uuid}: {reason}'
            )

        return response

    def set_uri_canonical_value(self, work_uuid, uri, canonical=False):
        """Set or unset URI for a work as canonical.

        Args:
            work_uuid (str): UUID of work in the translator database.
            uri (str): new URI to send.
            canonical (bool): Set True if the uri is the canonical identifier.
        """
        data = {
            'UUID': work_uuid,
            'URI': self.format_uri(uri),
            'canonical': canonical,
        }
        response = self.patch(self.uris_endpoint, params=data)

        if response.status_code not in (200, 201):
            reason = response.content.decode('utf-8')
            logger.error(
                f'Failed to update work {work_uuid} with URI {uri}: {reason}'
            )

        return response

    def post_multiple_uris(self, work_uuid, uris, canonical_uris=None):
        """Post multiple URIs for a work, without posting duplicates.

        Args:
            work_uuid (str): UUID of work in the translator database.
            uris (list): New URIs to send.
            canonical_uris (list): New canonical URIs to send.
        """
        if canonical_uris is None:
            canonical_uris = []

        work_uris = set(self.get_work_uris(work_uuid))
        new_uris = list(set(uris).difference(work_uris))
        new_canonical_uris = list(set(canonical_uris).difference(work_uris))

        for uri in new_uris:
            logger.info(f'Adding new URI {uri} to work {work_uuid}')
            self.post_new_uri(work_uuid, uri)

        for uri in new_canonical_uris:
            logger.info(f'Adding canonical URI {uri} to work {work_uuid}')
            self.post_new_uri(work_uuid, uri, canonical=True)

    def post_new_title(self, work_uuid, title):
        """Post new Title to the translator for a given work.

        Args:
            work_uuid (str): uuid of work to add new title to.
            title (dict):  new Uri to send, including UUID of work.
        """
        data = {'UUID': work_uuid, 'title': title}
        self.post(self.titles_endpoint, json=data)

    def _prepare_new_work(self, work_type, title, uris, canonical_uris):
        """Package work with the correct keys."""
        uris = [{'URI': self.format_uri(uri)} for uri in uris]
        uris.extend(
            [  # noqa
                {'URI': self.format_uri(uri), 'canonical': True}
                for uri in canonical_uris
            ]
        )
        return {
            'type': work_type,
            'title': title,
            'uri': uris,
        }

    def post_new_work(
            self,
            main_identifier,
            work_type,
            title,
            uris,
            canonical_uris=None
    ):
        """Post a new work to the translator.

        Args:
            main_identifier: E.g. DOI to test if the work is already present
                             in the translator DB.
            work_type (str): Type of work (book, journal-article, etc).
            title (str): Title of the work.
            uris (list): All URIs to register.
            canonical_uris (list): URIs to register as canonical.

        Note: There is nothing in the Translation service that prevents you
        from submitting duplicate works, so for now we need to check a main
        identifier before submitting a work to the API :/

        Note: The main use of the translator will be to fetch the canonical
        identifier that is assigned to a work so that metrics can be saved
        against that identifier. As such, 1) the main_identifier in this
        function will be set as the canonical identifier for that work
        scheme, by default, so 2) make sure that for this use case that the
        main_identifier supplied is the canonical identifier for a work of
        the scheme provided.
        """
        if canonical_uris is None:
            canonical_uris = []
        if main_identifier not in canonical_uris:
            canonical_uris.append(main_identifier)

        for uri in canonical_uris:  # remove canonical uris from other uris.
            if uri in uris:
                uris.remove(uri)

        data = self._prepare_new_work(work_type, title, uris, canonical_uris)
        work_exists, work_uuid = self.work_exists(
            main_identifier,
            self.get_scheme_from_uri(main_identifier)
        )

        if work_exists:
            logger.info(f"Work matching '{main_identifier}' already exists.")
            return self.post_multiple_uris(work_uuid, uris, canonical_uris)

        logger.info(f'Posting new work: {data}')
        response = self.post(self.works_endpoint, json=data)

        if response.status_code != 200:
            raise ValueError(response.content.decode('utf-8'))

    def delete_work(self, work_uuid):
        """Delete a work from the translator.

        Args:
            work_uuid (str): UUID of work to delete

        Returns:
            requests.Response: Response from the API

        Note, the translator will always return a 404 even if the work does
        exist and was deleted so returning a status code probably isn't worth
        much...
        """
        self.delete(self.works_endpoint, params={'uuid': work_uuid})
