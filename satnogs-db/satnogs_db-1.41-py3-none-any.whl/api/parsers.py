"""SatNOGS DB django rest framework API custom parsers"""
from pyld import jsonld
from rest_framework.parsers import JSONParser

from db.base.structured_data import get_structured_data


class JSONLDParser(JSONParser):  # pylint: disable=R0903
    """ Parser for JSONLD. """

    media_type = 'application/ld+json'

    def parse(self, stream, media_type=None, parser_context=None):
        """ Render `data` into JSONLD, returning a bytestring. """
        raw_data = super().parse(stream, media_type, parser_context)
        structured_data = get_structured_data(parser_context['view'].basename, [])
        data = jsonld.frame(raw_data, structured_data.frame, {'omitGraph': False})
        return data
