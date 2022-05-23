# -*- coding: utf-8 -*-
from cgbeacon2.utils.md5 import md5_key


class Variant:
    """A variant object"""

    def __init__(self, parsed_variant, dataset_ids, genome_assembly="GRCh37") -> None:
        self.referenceName = parsed_variant["chromosome"]  # Accepting values 1-22, X, Y, MT
        if parsed_variant.get("mate_name"):
            self.mateName = parsed_variant["mate_name"]
        self.start = parsed_variant[
            "start"
        ]  # int, Precise start coordinate position, allele locus (0-based, inclusive)
        self.end = parsed_variant["end"]  # int
        self.referenceBases = "".join(parsed_variant["reference_bases"])  # str, '^([ACGT]+|N)$'
        self.alternateBases = "".join(parsed_variant["alternate_bases"])  # str, '^([ACGT]+|N)$'
        if parsed_variant.get("variant_type"):
            self.variantType = parsed_variant[
                "variant_type"
            ]  # is used to denote structural variants: 'INS', 'DUP', 'DEL', 'INV'
        self.assemblyId = genome_assembly  # str
        self.datasetIds = dataset_ids  # list of dictionaries, i.e. [{ dataset_id: { samples : [list of samples]}  }]
        self._id = md5_key(
            self.referenceName,
            self.start,
            self.end,
            self.referenceBases,
            self.alternateBases,
            genome_assembly,
        )
