"""Provide miscellaneous tools for fusion modeling."""
from biocommons.seqrepo.seqrepo import SeqRepo
from ga4gh.vrsatile.pydantic.vrs_models import CURIE

from fusor import logger
from fusor.exceptions import IDTranslationException


def translate_identifier(seqrepo: SeqRepo, ac: str,
                         target_namespace: str = "ga4gh") -> CURIE:
    """Return `target_namespace` identifier for accession provided.

    :param str ac: Identifier accession
    :param str target_namespace: The namespace of identifiers to return.
        Default is `ga4gh`
    :return: Identifier for `target_namespace`
    :raise: IDTranslationException if unable to perform desired translation
    """
    try:
        target_ids = seqrepo.translate_identifier(
            ac, target_namespaces=target_namespace)
    except KeyError as e:
        logger.warning(f"Unable to get translated identifier: {e}")
        raise IDTranslationException

    if target_ids:
        return target_ids[0]
    else:
        raise IDTranslationException
