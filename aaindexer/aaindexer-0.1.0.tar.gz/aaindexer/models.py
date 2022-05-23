"""
Pydantic classes
"""
from pydantic import BaseModel
from typing import Optional


class AaindexRecord(BaseModel):
    """
    A single record from a single aaindex database
    """
    #: Record accession, e.g. ``"ANDN920101"``
    accession: str
    #: Record description, as a string, e.g.
    #: ``"alpha-CH chemical shifts (Andersen et al., 1992)"``
    description: str
    #: PubMed identifier, e.g. ``"PMID:1575719"``
    pmid: Optional[str]
    #: Authors for the source publication, as a single string, e.g.
    #: ``"Andersen, N.H., Cao, B. and Chen, C."``
    authors: Optional[str]
    #: Title of the source publication, e.g. ``"Peptide/protein structure analysis
    #: using the chemical shift index method:
    #: upfield alpha-CH values reveal dynamic helices and aL sites"``
    title: Optional[str]
    #: Journal for the source publication, e.g. ``"Biochem. and Biophys. Res. Comm. 184,
    #: 1008-1014 (1992)"``
    journal: Optional[str]
    #: Additional comments
    comment: Optional[str]
    #: A dictionary of correlations between this record and others in the same database.
    #: The dictionary is indexed by the record accession number.
    #: e.g. ``{ "ROBB760101": 0.874, "QIAN880106": 0.846 }``
    correlation: Optional[dict[str, Optional[float]]]
    #: A dictionary indexed by amino acid 1-letter codes, where the values are
    #: amino acid properties described in this record.
    #: e.g. ``{"A": 0.68, "R": -0.22 }``
    index: Optional[dict[str, Optional[float]]]
    #: A dictionary of dictionaries. The first and second index are both amino acid
    #: 1-letter codes, defining up a substitution matrix between the two amino acids.
    #: e.g. ``{ "A": { "A": 3.0 }, "R": { "A": -3.0, "R": 6.0 }``.
    #: Note that if matrix[X][Y] is not defined, then matrix[Y][X] (the reverse) will
    #: be.
    matrix: Optional[dict[str, dict[str, Optional[float]]]]
