"""Provide helper methods for fusion nomenclature generation."""
from biocommons.seqrepo.seqrepo import SeqRepo
from ga4gh.vrsatile.pydantic.vrs_models import SequenceLocation
from fusor.exceptions import IDTranslationException

from fusor.models import GeneElement, RegulatoryElement, \
    TemplatedSequenceElement, TranscriptSegmentElement
from fusor.tools import translate_identifier


def reg_element_nomenclature(element: RegulatoryElement, sr: SeqRepo) -> str:
    """Return fusion nomenclature for regulatory element.
    :param RegulatoryElement element: a regulatory element object
    :param SeqRepo sr: a SeqRepo instance
    :return: regulatory element nomenclature representation
    :raises ValueError: if unable to retrieve genomic location or coordinates,
        or if missing element reference ID, genomic location, and associated
        gene
    """
    nm_type_string = f"reg_{element.regulatory_class.value}"
    nm_string = ""
    if element.feature_id:
        nm_string += f"_{element.feature_id}"
    elif element.genomic_location:
        start = element.genomic_location
        sequence_id = start.location.sequence_id
        refseq_id = translate_identifier(sr, sequence_id, "refseq")
        try:
            chr = str(
                translate_identifier(sr, sequence_id, "GRCh38")
            ).split(":")[1]
        except IDTranslationException:
            raise ValueError
        nm_string += f"_{refseq_id}(chr {chr}):g.{start.location.interval.start.value}_{start.location.interval.end.value}"  # noqa: E501
    if element.associated_gene:
        if element.associated_gene.gene_id:
            gene_id = gene_id = element.associated_gene.gene_id

        if element.associated_gene.gene_id:
            gene_id = element.associated_gene.gene_id
        elif element.associated_gene.gene and \
                element.associated_gene.gene.gene_id:
            gene_id = element.associated_gene.gene.gene_id
        else:
            raise ValueError
        nm_string += f"@{element.associated_gene.label}({gene_id})"
    if not nm_string:
        raise ValueError
    return nm_type_string + nm_string


def tx_segment_nomenclature(element: TranscriptSegmentElement,
                            first: bool,
                            last: bool) -> str:
    """Return fusion nomenclature for transcript segment element
    :param TranscriptSegmentElement element: a tx segment element
    :param bool first: True if first element in sequence
    :param bool last: True if last element in sequence
    :return: element nomenclature representation
    """
    prefix = f"{element.transcript}({element.gene_descriptor.label})"
    start, start_offset, end, end_offset = "", "", "", ""
    if not first:
        start = element.exon_start
        if element.exon_start_offset:
            start_offset = element.exon_start_offset
    if not last:
        end = element.exon_end
        if element.exon_end_offset:
            end_offset = element.exon_end_offset
    return f"{prefix}:e.{start}{start_offset}_{end}{end_offset}"


def templated_seq_nomenclature(element: TemplatedSequenceElement,
                               sr: SeqRepo) -> str:
    """Return fusion nomenclature for templated sequence element.
    :param TemplatedSequenceElement element: a templated sequence element
    :return: element nomenclature representation
    :raises ValueError: if location isn't a SequenceLocation or if unable
    to retrieve region or location
    """
    if element.region and element.region.location:
        location = element.region.location
        if isinstance(location, SequenceLocation):
            sequence_id = str(location.sequence_id)
            refseq_id = translate_identifier(sr, sequence_id, "refseq")
            start = location.interval.start.value
            end = location.interval.end.value
            try:
                chr = str(
                    translate_identifier(sr, sequence_id, "GRCh38")
                ).split(":")[1]
            except IDTranslationException:
                raise ValueError
            return f"{refseq_id}(chr {chr}):g.{start}_{end}({element.strand.value})"
        else:
            raise ValueError
    else:
        raise ValueError


def gene_nomenclature(element: GeneElement) -> str:
    """Return fusion nomenclature for gene element.
    :param GeneElement element: a gene element object
    :return: element nomenclature representation
    :raises ValueError: if unable to retrieve gene ID
    """
    if element.gene_descriptor.gene_id:
        gene_id = gene_id = element.gene_descriptor.gene_id

    if element.gene_descriptor.gene_id:
        gene_id = element.gene_descriptor.gene_id
    elif element.gene_descriptor.gene \
            and element.gene_descriptor.gene.gene_id:
        gene_id = element.gene_descriptor.gene.gene_id
    else:
        raise ValueError
    return f"{element.gene_descriptor.label}({gene_id})"
