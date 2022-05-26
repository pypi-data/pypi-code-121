"""Module for modifying fusion objects."""
from typing import Optional, List, Tuple, Dict
from urllib.parse import quote

from biocommons.seqrepo import SeqRepo
from bioutils.accessions import coerce_namespace
from ga4gh.core import ga4gh_identify
from ga4gh.vrs import models
from ga4gh.vrsatile.pydantic.vrs_models import CURIE, VRSTypes, \
    SequenceLocation, Number, SequenceInterval
from ga4gh.vrsatile.pydantic.vrsatile_models import GeneDescriptor,\
    LocationDescriptor
from pydantic.error_wrappers import ValidationError
from uta_tools.uta_tools import UTATools
from uta_tools.schemas import ResidueMode
from gene.query import QueryHandler

from fusor import SEQREPO_DATA_PATH, UTA_DB_URL, logger
from fusor.models import AssayedFusion, AssayedFusionElements, \
    CategoricalFusion, CategoricalFusionElements, BaseStructuralElement, \
    StructuralElementType, Event, Evidence, Fusion, MolecularAssay, \
    TemplatedSequenceElement, AdditionalFields, TranscriptSegmentElement, \
    GeneElement, LinkerElement, UnknownGeneElement, MultiplePossibleGenesElement, \
    RegulatoryElement, DomainStatus, FunctionalDomain, Strand, \
    RegulatoryClass, FusionType
from fusor.nomenclature import reg_element_nomenclature, \
    tx_segment_nomenclature, templated_seq_nomenclature, gene_nomenclature
from fusor.exceptions import IDTranslationException
from fusor.tools import translate_identifier


class FUSOR:
    """Class for modifying fusion objects."""

    def __init__(self,
                 seqrepo_data_path: str = SEQREPO_DATA_PATH,
                 dynamodb_url: str = "",
                 dynamodb_region: str = "us-east-2",
                 db_url: str = UTA_DB_URL, db_pwd: str = "",
                 ) -> None:
        """Initialize FUSOR class.

        :param str seqrepo_data_path: Path to SeqRepo data directory
        :param str dynamodb_url: URL to gene-normalizer database source.
            Can also set environment variable `GENE_NORM_DB_URL`.
        :param str dynamodb_region: AWS default region for gene-normalizer.
        :param str db_url: Postgres URL for UTA
        :param str db_pwd: Postgres database password
        """
        self.seqrepo = SeqRepo(seqrepo_data_path)
        self.gene_normalizer = QueryHandler(
            db_url=dynamodb_url, db_region=dynamodb_region)
        self.uta_tools = UTATools(db_url=db_url, db_pwd=db_pwd)

    @staticmethod
    def _contains_element_type(kwargs: Dict, elm_type: StructuralElementType) -> bool:
        """Check if fusion contains element of a specific type. Helper method
        for inferring fusion type.
        :param Dict kwargs: keyword args given to fusion method
        :param StructuralElementType elm_type: element type to match
        :return: True if at least one element of given type is found,
        False otherwise.
        """
        for c in kwargs["structural_elements"]:
            if isinstance(c, Dict) and c.get("type") == elm_type:
                return True
            elif isinstance(c, BaseStructuralElement) and c.type == elm_type:
                return True
        return False

    def fusion(self, fusion_type: Optional[FusionType] = None,
               **kwargs) -> Tuple[Optional[Fusion], Optional[str]]:
        """Construct fusion object.

        :param Optional[FusionType] fusion_type: explicitly specify fusion type.
            Unecessary if providing fusion object in keyword args that includes `type`
            attribute.
        :return: Tuple containing optional Fusion if construction successful, and any
            relevant warnings
        """
        # try explicit type param
        explicit_type = kwargs.get("type")
        if not fusion_type and explicit_type:
            if explicit_type in FusionType.values():
                fusion_type = explicit_type
                kwargs.pop("type")
            else:
                return (None, f"Invalid type parameter: {explicit_type}")
        if fusion_type:
            if fusion_type == FusionType.CATEGORICAL_FUSION:
                return self.categorical_fusion(**kwargs)
            elif fusion_type == FusionType.ASSAYED_FUSION:
                return self.assayed_fusion(**kwargs)
            else:
                return (None, f"Invalid fusion_type parameter: {fusion_type}")

        # try to infer from provided attributes
        categorical_attributes = any([
            "critical_functional_domains" in kwargs,
            "r_frame_preserved" in kwargs,
            self._contains_element_type(
                kwargs, StructuralElementType.MULTIPLE_POSSIBLE_GENES_ELEMENT
            )
        ])
        assayed_attributes = any([
            "causative_event" in kwargs,
            "event_description" in kwargs,
            "fusion_evidence" in kwargs,
            "molecular_assay" in kwargs,
            self._contains_element_type(kwargs,
                                        StructuralElementType.UNKNOWN_GENE_ELEMENT)
        ])
        if categorical_attributes and not assayed_attributes:
            return self.categorical_fusion(**kwargs)
        elif assayed_attributes and not categorical_attributes:
            return self.assayed_fusion(**kwargs)
        if categorical_attributes and assayed_attributes:
            return None, "Received conflicting attributes"
        else:
            return None, "Unable to determine fusion type"

    @staticmethod
    def categorical_fusion(
        structural_elements: CategoricalFusionElements,
        regulatory_elements: Optional[List[RegulatoryElement]] = None,
        critical_functional_domains: Optional[List[FunctionalDomain]] = None,
        r_frame_preserved: Optional[bool] = None
    ) -> Tuple[Optional[CategoricalFusion], Optional[str]]:
        """Construct a categorical fusion object
        :param CategoricalFusionElements structural_elements: elements
            constituting the fusion
        :param Optional[RegulatoryElement] regulatory_elements: affected
            regulatory elements
        :param Optional[List[FunctionalDomain]] domains: lost or preserved
            functional domains
        :param Optional[bool] r_frame_preserved: `True` if reading frame is
            preserved.  `False` otherwise
        :return: Tuple containing optional CategoricalFusion if construction
        successful, and any relevant validation warnings
        """
        try:
            fusion = CategoricalFusion(
                structural_elements=structural_elements,
                critical_functional_domains=critical_functional_domains,
                r_frame_preserved=r_frame_preserved,
                regulatory_elements=regulatory_elements
            )
        except ValidationError as e:
            return None, str(e)
        return fusion, None

    @staticmethod
    def assayed_fusion(
        structural_elements: AssayedFusionElements,
        regulatory_elements: Optional[List[RegulatoryElement]] = None,
        causative_event: Optional[Event] = None,
        fusion_evidence: Optional[Evidence] = None,
        molecular_assay: Optional[MolecularAssay] = None,
    ) -> Tuple[Optional[AssayedFusion], Optional[str]]:
        """Construct an assayed fusion object
        :param AssayedFusionElements structural_elements: elements constituting the
            fusion
        :param Optional[RegulatoryElement] regulatory_elements: affected regulatory
            elements
        :param Optional[Event] causative_event: event causing the fusion, if known
        :param Optional[Evidence] fusion_evidence: whether the fusion is inferred or
            directly observed
        :param Optional[MolecularAssay] molecular_assay: how knowledge of the fusion
            was obtained
        :return: Tuple containing optional AssayedFusion if construction successful,
            and any relevant validation warnings
        """
        try:
            fusion = AssayedFusion(
                structural_elements=structural_elements,
                regulatory_elements=regulatory_elements,
                causative_event=causative_event,
                fusion_evidence=fusion_evidence,
                molecular_assay=molecular_assay
            )
        except ValidationError as e:
            return None, str(e)
        return fusion, None

    async def transcript_segment_element(
            self, tx_to_genomic_coords: bool = True,
            use_minimal_gene_descr: bool = True,
            seq_id_target_namespace: Optional[str] = None,
            **kwargs
    ) -> Tuple[Optional[TranscriptSegmentElement], Optional[List[str]]]:
        """Create transcript segment element

        :param bool tx_to_genomic_coords: `True` if going from transcript
            to genomic coordinates. `False` if going from genomic to
            transcript exon coordinates.
        :param bool use_minimal_gene_descr: `True` if minimal gene descriptor
            (`id`, `gene_id`, `label`) will be used. `False` if
            gene-normalizer's gene descriptor will be used
        :param Optional[str] seq_id_target_namespace: If want to use digest for
            `sequence_id`, set this to the namespace you want the digest for.
            Otherwise, leave as `None`.
        :param kwargs:
            If `tx_to_genomic_coords`, possible key word arguments:
                (From uta_tools.transcript_to_genomic_coords)
                gene: Optional[str] = None, transcript: str = None,
                exon_start: Optional[int] = None,
                exon_start_offset: Optional[int] = 0,
                exon_end: Optional[int] = None,
                exon_end_offset: Optional[int] = 0
            else:
                (From uta_tools.genomic_to_transcript_exon_coordinates)
                chromosome: Union[str, int], start: Optional[int] = None,
                end: Optional[int] = None, strand: Optional[int] = None,
                transcript: Optional[str] = None, gene: Optional[str] = None,
                residue_mode: ResidueMode = ResidueMode.RESIDUE
        :return: Transcript Segment Element, warning
        """
        if tx_to_genomic_coords:
            data = await self.uta_tools.transcript_to_genomic_coordinates(**kwargs)  # noqa: E501
        else:
            if "chromosome" in kwargs and kwargs.get("chromosome") is None:
                msg = "`chromosome` is required when going from genomic to" \
                      " transcript exon coordinates"
                logger.warning(msg)
                return None, [msg]
            residue_mode = kwargs.get("residue_mode")
            # TODO: Remove once fixed in uta_tools
            if residue_mode != ResidueMode.INTER_RESIDUE:
                start = kwargs.get("start")
                kwargs["start"] = start - 1 if start is not None else None
                kwargs["residue_mode"] = "inter-residue"
            data = await self.uta_tools.genomic_to_transcript_exon_coordinates(**kwargs)  # noqa: E501

        if data.genomic_data is None:
            return None, data.warnings

        genomic_data = data.genomic_data
        genomic_data.transcript = coerce_namespace(genomic_data.transcript)

        normalized_gene_response = self._normalized_gene_descriptor(
            genomic_data.gene,
            use_minimal_gene_descr=use_minimal_gene_descr)
        if not normalized_gene_response[0] and normalized_gene_response[1]:
            return None, [normalized_gene_response[1]]

        return TranscriptSegmentElement(
            transcript=genomic_data.transcript,
            exon_start=genomic_data.exon_start,
            exon_start_offset=genomic_data.exon_start_offset,
            exon_end=genomic_data.exon_end,
            exon_end_offset=genomic_data.exon_end_offset,
            gene_descriptor=normalized_gene_response[0],
            element_genomic_start=self._location_descriptor(
                genomic_data.start, genomic_data.start + 1, genomic_data.chr,
                label=genomic_data.chr,
                seq_id_target_namespace=seq_id_target_namespace) if genomic_data.start else None,  # noqa: E501
            element_genomic_end=self._location_descriptor(
                genomic_data.end, genomic_data.end + 1, genomic_data.chr,
                label=genomic_data.chr,
                seq_id_target_namespace=seq_id_target_namespace) if genomic_data.end else None,  # noqa: E501
        ), None

    def gene_element(
            self, gene: str,
            use_minimal_gene_descr: bool = True
    ) -> Tuple[Optional[GeneElement], Optional[str]]:
        """Create gene element

        :param str gene: Gene
        :param bool use_minimal_gene_descr: `True` if minimal gene descriptor
            (`id`, `gene_id`, `label`) will be used. `False` if
            gene-normalizer's gene descriptor will be used
        :return: GeneElement, warning
        """
        gene_descr, warning = self._normalized_gene_descriptor(
            gene, use_minimal_gene_descr=use_minimal_gene_descr)
        if not gene_descr:
            return None, warning
        else:
            return GeneElement(gene_descriptor=gene_descr), None

    def templated_sequence_element(
            self, start: int, end: int, sequence_id: str, strand: Strand,
            label: Optional[str] = None, add_location_id: bool = False,
            residue_mode: ResidueMode = ResidueMode.RESIDUE,
            seq_id_target_namespace: Optional[str] = None
    ) -> TemplatedSequenceElement:
        """Create templated sequence element

        :param int start: Genomic start
        :param int end: Genomic end
        :param str sequence_id: Chromosome accession for sequence
        :param Strand strand: Strand
        :param Optional[str] label: Label for genomic location
        :param bool add_location_id: `True` if `location_id` will be added
            to `region`. `False` otherwise.
        :param ResidueMode residue_mode: Determines coordinate base used.
            Must be one of `residue` or `inter-residue`.
        :param Optional[str] seq_id_target_namespace: If want to use digest for
            `sequence_id`, set this to the namespace you want the digest for.
            Otherwise, leave as `None`.
        :return: Templated Sequence Element
        """
        if residue_mode == ResidueMode.RESIDUE:
            start -= 1

        region = self._location_descriptor(
            start, end, sequence_id, label=label,
            seq_id_target_namespace=seq_id_target_namespace)

        if add_location_id:
            location_id = self._location_id(region.location.dict())
            region.location_id = location_id

        return TemplatedSequenceElement(region=region, strand=strand)

    @staticmethod
    def linker_element(
        sequence: str,
        residue_type: CURIE = "SO:0000348"  # type: ignore
    ) -> Tuple[Optional[LinkerElement], Optional[str]]:
        """Create linker element

        :param str sequence: Sequence
        :param CURIE residue_type: Sequence Ontology code for residue type of
            `sequence`
        :return: Tuple containing a complete Linker element and None if
            successful, or a None value and warning message if unsuccessful
        """
        try:
            seq = sequence.upper()
            params = {
                "linker_sequence": {
                    "id": f"fusor.sequence:{seq}",
                    "sequence": seq,
                    "residue_type": residue_type
                }
            }
            return LinkerElement(**params), None
        except ValidationError as e:
            msg = str(e)
            logger.warning(msg)
            return None, msg

    @staticmethod
    def multiple_possible_genes_element() -> MultiplePossibleGenesElement:
        """Create a MultiplePossibleGenesElement.

        :return: MultiplePossibleGenesElement
        """
        return MultiplePossibleGenesElement()

    @staticmethod
    def unknown_gene_element() -> UnknownGeneElement:
        """Create unknown gene element

        :return: Unknown Gene element
        """
        return UnknownGeneElement()

    def functional_domain(
            self, status: DomainStatus, name: str,
            functional_domain_id: CURIE, gene: str,
            sequence_id: str, start: int, end: int,
            use_minimal_gene_descr: bool = True,
            seq_id_target_namespace: Optional[str] = None,
    ) -> Tuple[Optional[FunctionalDomain], Optional[str]]:
        """Build functional domain instance.

        :param DomainStatus status: Status for domain.  Must be either `lost`
            or `preserved`
        :param str name: Domain name
        :param CURIE functional_domain_id: Domain ID
        :param str gene: Gene
        :param str sequence_id: protein sequence on which provided coordinates
            are located
        :param int start: start position on sequence
        :param in end: end position on sequence
        :param bool use_minimal_gene_descr: `True` if minimal gene descriptor
            (`id`, `gene_id`, `label`) will be used. `False` if
            gene-normalizer's gene descriptor will be used
        :param Optional[str] seq_id_target_namespace: If want to use digest for
            `sequence_id`, set this to the namespace you want the digest for.
            Otherwise, leave as `None`.
        :return: Tuple with FunctionalDomain and None value for warnings if
            successful, or a None value and warning message if unsuccessful
        """
        sequence_id_lower = sequence_id.lower()
        if not (sequence_id_lower.startswith("np_")) or \
                (sequence_id_lower.startswith("ensp")):
            msg = "Sequence_id must be a protein accession."
            logger.warning(msg)
            return None, msg

        valid = self.uta_tools.seqrepo_access.is_valid_input_sequence(
            sequence_id, start, end
        )

        if not valid[0]:
            return None, valid[1]

        gene_descr, warning = self._normalized_gene_descriptor(
            gene, use_minimal_gene_descr=use_minimal_gene_descr)
        if not gene_descr:
            return None, warning

        loc_descr = self._location_descriptor(
            start, end, sequence_id,
            seq_id_target_namespace=seq_id_target_namespace
        )

        try:
            return FunctionalDomain(
                id=functional_domain_id,
                name=name,
                status=status,
                gene_descriptor=gene_descr,
                location_descriptor=loc_descr
            ), None
        except ValidationError as e:
            msg = str(e)
            logger.warning(msg)
            return None, msg

    def regulatory_element(
        self, regulatory_class: RegulatoryClass, gene: str,
        use_minimal_gene_descr: bool = True
    ) -> Tuple[Optional[RegulatoryElement], Optional[str]]:
        """Create RegulatoryElement
        :param RegulatoryClass regulatory_class: one of {"promoter", "enhancer"}
        :param str gene: gene term to fetch normalized descriptor for
        :return: Tuple with RegulatoryElement instance and None value for warnings if
            successful, or a None value and warning message if unsuccessful
        """
        gene_descr, warning = self._normalized_gene_descriptor(
            gene, use_minimal_gene_descr=use_minimal_gene_descr)
        if not gene_descr:
            return (None, warning)

        try:
            return RegulatoryElement(
                regulatory_class=regulatory_class,
                associated_gene=gene_descr
            ), None
        except ValidationError as e:
            msg = str(e)
            logger.warning(msg)
            return None, msg

    def _location_descriptor(
            self, start: int, end: int, sequence_id: str,
            label: Optional[str] = None,
            seq_id_target_namespace: Optional[str] = None,
            use_location_id: bool = False
    ) -> LocationDescriptor:
        """Create location descriptor

        :param int start: Start position
        :param int end: End position
        :param str sequence_id: Accession for sequence
        :param str label: label for location. If `None`, `sequence_id` will be used as
            Location Descriptor's `id` Else, label will be used as Location
            Descriptor's `id`.
        :param str seq_id_target_namespace: If want to use digest for `sequence_id`,
            set this to the namespace you want the digest for. Otherwise, leave as
            `None`.
        :param bool use_location_id: Takes precedence over `label` or `sequence_id`
            becoming Location Descriptor's id. `True` if  use ga4gh digest as Location
            Descriptor's id. `False`, use default of `label` > `sequence_id`
        """
        seq_id_input = sequence_id
        try:
            sequence_id = coerce_namespace(sequence_id)
        except ValueError:
            try:
                CURIE(__root__=sequence_id)
            except ValidationError:
                sequence_id = f"sequence.id:{sequence_id}"

        if seq_id_target_namespace:
            try:
                seq_id = translate_identifier(
                    self.seqrepo, sequence_id,
                    target_namespace=seq_id_target_namespace)
            except IDTranslationException:
                logger.warning(f"Unable to translate {sequence_id} using"
                               f" {seq_id_target_namespace} as the target"
                               f" namespace")
            else:
                sequence_id = seq_id

        location = SequenceLocation(
            sequence_id=sequence_id,
            interval=SequenceInterval(start=Number(value=start),
                                      end=Number(value=end))
        )

        if use_location_id:
            _id = self._location_id(location.dict())
        else:
            quote_id = quote(label) if label else quote(seq_id_input)
            _id = f"fusor.location_descriptor:{quote_id}"

        location_descr = LocationDescriptor(
            id=_id,
            location=location
        )

        if label:
            location_descr.label = label
        return location_descr

    def add_additional_fields(
            self, fusion: Fusion, add_all: bool = True,
            fields: Optional[List[AdditionalFields]] = None,
            target_namespace: str = "ga4gh"
    ) -> Fusion:
        """Add additional fields to Fusion object.
        Possible fields are shown in `AdditionalFields`

        :param Fusion fusion: A valid Fusion object
        :param bool add_all: `True` if all additional fields  will be added
            in fusion object. `False` if only select fields will be provided.
            If set to `True`, will always take precedence over `fields`.
        :param list fields: Select fields that will be set. Must be a subset of
            `AdditionalFields`
        :param str target_namespace: The namespace of identifiers to return
            for `sequence_id`. Default is `ga4gh`
        :return: Updated fusion with specified fields set
        """
        if add_all:
            self.add_translated_sequence_id(fusion, target_namespace)
            self.add_location_id(fusion)
        else:
            if fields:
                for field in fields:
                    if field == AdditionalFields.SEQUENCE_ID.value:
                        self.add_translated_sequence_id(
                            fusion, target_namespace=target_namespace)
                    elif field == AdditionalFields.LOCATION_ID.value:
                        self.add_location_id(fusion)
                    else:
                        logger.warning(f"Invalid field: {field}")
        return fusion

    def add_location_id(self, fusion: Fusion) -> Fusion:
        """Add `location_id` in fusion object.

        :param Fusion fusion: A valid Fusion object.
        :return: Updated fusion with `location_id` fields set
        """
        for structural_element in fusion.structural_elements:
            if isinstance(structural_element, TemplatedSequenceElement):
                location = structural_element.region.location
                location_id = self._location_id(location.dict())
                structural_element.region.location_id = location_id
            elif isinstance(structural_element, TranscriptSegmentElement):
                for element_genomic in [
                    structural_element.element_genomic_start,
                    structural_element.element_genomic_end
                ]:
                    if element_genomic:
                        location = element_genomic.location
                        if location.type == VRSTypes.SEQUENCE_LOCATION.value:
                            location_id = self._location_id(location.dict())
                            element_genomic.location_id = location_id
        if isinstance(fusion, CategoricalFusion) and fusion.critical_functional_domains:
            for domain in fusion.critical_functional_domains:
                location = domain.location_descriptor.location
                location_id = self._location_id(location.dict())
                domain.location_descriptor.location_id = location_id
        if fusion.regulatory_elements:
            for element in fusion.regulatory_elements:
                if element.genomic_location:
                    location = element.genomic_location
                    if location.type == VRSTypes.SEQUENCE_LOCATION.value:
                        location_id = self._location_id(location.dict())
                        element.genomic_location.location_id = location_id
        return fusion

    @staticmethod
    def _location_id(location: Dict) -> CURIE:
        """Return GA4GH digest for location

        :param dict location: VRS Location represented as a dict
        :return: GA4GH digest
        """
        return ga4gh_identify(models.Location(**location))

    def add_translated_sequence_id(self, fusion: Fusion,
                                   target_namespace: str = "ga4gh") -> Fusion:
        """Translate sequence_ids in fusion object.

        :param Fusion fusion: A valid Fusion object
        :param str target_namespace: ID namespace to translate sequence IDs to
        :return: Updated fusion with `sequence_id` fields set
        """
        for element in fusion.structural_elements:
            if isinstance(element, TemplatedSequenceElement):
                location = element.region.location
                if location.type == VRSTypes.SEQUENCE_LOCATION.value:
                    try:
                        new_id = translate_identifier(
                            self.seqrepo, location.sequence_id,
                            target_namespace
                        )
                    except IDTranslationException:
                        pass
                    else:
                        element.region.location.sequence_id = new_id
            elif isinstance(element, TranscriptSegmentElement):
                for loc_descr in [
                    element.element_genomic_start,
                    element.element_genomic_end
                ]:
                    if loc_descr:
                        location = loc_descr.location
                        if location.type == VRSTypes.SEQUENCE_LOCATION.value:
                            try:
                                new_id = translate_identifier(
                                    self.seqrepo, location.sequence_id,
                                    target_namespace
                                )
                            except IDTranslationException:
                                continue
                            loc_descr.location.sequence_id = new_id
        if fusion.type == "CategoricalFusion" and fusion.critical_functional_domains:
            for domain in fusion.critical_functional_domains:
                if (
                    domain.location_descriptor
                    and domain.location_descriptor.location
                    and (domain.location_descriptor.location.type ==
                         "SequenceLocation")
                ):
                    try:
                        new_id = translate_identifier(
                            self.seqrepo,
                            domain.location_descriptor.location.sequence_id,
                            target_namespace
                        )
                    except IDTranslationException:
                        continue
                    domain.location_descriptor.location.sequence_id = new_id
        return fusion

    def add_gene_descriptor(self, fusion: Fusion) -> Fusion:
        """Add additional fields to `gene_descriptor` in fusion object

        :param Fusion fusion: A valid Fusion object
        :return: Updated fusion with additional fields set in `gene_descriptor`
        """
        fields = [
            (fusion.structural_elements, "gene_descriptor"),
            (fusion.regulatory_elements, "associated_gene")
        ]
        if fusion.type == FusionType.CATEGORICAL_FUSION:
            fields.append((fusion.critical_functional_domains, "gene_descriptor"))
        for (property, field_name) in fields:
            for obj in property:
                if field_name in obj.__fields__.keys():
                    label = obj.__getattribute__(field_name).label
                    norm_gene_descr, _ = self._normalized_gene_descriptor(
                        label, use_minimal_gene_descr=False)
                    if norm_gene_descr:
                        obj.__setattr__(field_name, norm_gene_descr)
        return fusion

    def _normalized_gene_descriptor(
            self, query: str,
            use_minimal_gene_descr: bool = True
    ) -> Tuple[Optional[GeneDescriptor], Optional[str]]:
        """Return gene descriptor from normalized response.

        :param str query: Gene query
        :param bool use_minimal_gene_descr: `True` if minimal gene descriptor
            (`id`, `gene_id`, `label`) will be used. `False` if
            gene-normalizer's gene descriptor will be used
        :return: Tuple with gene descriptor and None value for warnings if
            successful, and None value with warning string if unsuccessful
        """
        gene_norm_resp = self.gene_normalizer.normalize(query)
        if gene_norm_resp.match_type:
            gene_descr = gene_norm_resp.gene_descriptor
            if use_minimal_gene_descr:
                gene_descr = GeneDescriptor(
                    id=gene_descr.id,
                    gene_id=gene_descr.gene_id,
                    label=gene_descr.label
                )
            return gene_descr, None
        else:
            return None, f"gene-normalizer unable to normalize {query}"

    def generate_nomenclature(self, fusion: Fusion) -> str:
        """Generate human-readable nomenclature describing provided fusion
        :param Fusion fusion: a valid fusion
        :return: string summarizing fusion in human-readable way per
            VICC fusion curation nomenclature
        """
        parts = []
        element_genes = []
        if fusion.regulatory_elements:
            num_reg_elements = len(fusion.regulatory_elements)
            for element in fusion.regulatory_elements:
                parts.append(reg_element_nomenclature(element, self.seqrepo))
                if element.associated_gene:
                    element_genes.append(element.associated_gene.label)
        else:
            num_reg_elements = 0
        for i, element in enumerate(fusion.structural_elements):
            if isinstance(element, MultiplePossibleGenesElement):
                parts.append("v")
            elif isinstance(element, UnknownGeneElement):
                parts.append("?")
            elif isinstance(element, LinkerElement):
                parts.append(element.linker_sequence.sequence)
            elif isinstance(element, TranscriptSegmentElement):
                if not any([gene == element.gene_descriptor.label
                            for gene in element_genes]):
                    parts.append(tx_segment_nomenclature(
                        element,
                        first=(i + num_reg_elements == 0),
                        last=(i + 1 == len(fusion.structural_elements))
                    ))
            elif isinstance(element, TemplatedSequenceElement):
                parts.append(templated_seq_nomenclature(element,
                                                        self.seqrepo))
            elif isinstance(element, GeneElement):
                if not any([gene == element.gene_descriptor.label
                            for gene in element_genes]):
                    parts.append(gene_nomenclature(element))
            else:
                raise ValueError
        return "::".join(parts)
