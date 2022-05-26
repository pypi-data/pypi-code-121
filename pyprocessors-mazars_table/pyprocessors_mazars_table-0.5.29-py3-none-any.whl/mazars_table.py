from collections import defaultdict
from enum import Enum
from functools import reduce
from itertools import groupby
from typing import List, Type, cast

from pydantic import Field, BaseModel
from pymultirole_plugins.v1.processor import ProcessorParameters, ProcessorBase
from pymultirole_plugins.v1.schema import Annotation, Document, AltText

from .normalizers import (
    CleanText,
    CleanDate,
    NormalizeDate,
    NormalizeDuration,
    CleanAmount,
    NormalizeAmount,
    NormalizeIndex,
    CleanIndex,
    CleanDuration,
)
from .reducers import Deduplicate, FuzzyDeduplicate, MostRecent, GreaterThan30


class OutputFormat(str, Enum):
    xlsx = "xlsx"


class MazarsTableParameters(ProcessorParameters):
    format: OutputFormat = Field(OutputFormat.xlsx, description="Output format")
    as_altText: str = Field(
        "slots",
        description="""If defined generate the slots as an alternative text of the input document,
    if not replace the text of the input document.""",
    )


def compose(*functions):
    return reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)


def compose_functions(functions):
    composed_fun = (
        compose(*reversed(functions)) if isinstance(functions, List) else functions
    )
    return composed_fun


Labels = {
    "bailleur": "Bailleur",
    "preneur": "Preneur",
    "indexation": "Indexation",
    "dureetotale": "DuréeTotale",
    "dated_effet": "Dated'Effet (date)",
    "montantduloyer": "MontantduLoyer",
    "franchise": "Franchise (en mois)",
    "depotgarantie_lettre": "DépôtdeGarantie (en lettre)",
    "adresse": "Adresse",
    "preavis": "Preavis",
    "dateeffet_lettres": "Dated'Effet (en lettre)",
    "duree_ferme": "DuréeFerme",
    "dureederenouvellement": "Dureederenouvellement",
    "depotdegarantie": "DépôtdeGarantie",
    "franchise_chiffre": "Franchise (chiffre)",
    "redevance_rie": "RedevanceRIE",
    "chargesannuelles": "ChargesAnnuelles",
    "chargestrimestrielles": "ChargesTrimestrielles",
    "provisionpourimpots": "ProvisionpourImpôts"
}

Normalizers = {
    "Bailleur": [
        CleanText,
    ],
    "Preneur": [
        CleanText,
    ],
    "Adresse": [
        CleanText,
    ],
    "Dated'Effet (date)": [
        CleanDate,
        NormalizeDate,
    ],
    "Dated'Effet (en lettre)": [CleanText, NormalizeDate],
    "DuréeTotale": [CleanDuration, NormalizeDuration],
    "DuréeFerme": [CleanDuration, NormalizeDuration],
    "MontantduLoyer": [CleanAmount, NormalizeAmount],
    "DépôtdeGarantie": [CleanText, NormalizeDuration],
    "DépôtdeGarantie (en lettre)": [CleanText, NormalizeDuration],
    "Franchise (en mois)": [CleanText, NormalizeDuration],
    "Franchise (chiffre)": [CleanAmount, NormalizeAmount],
    "Indexation": [CleanIndex, NormalizeIndex],
    "Preavis": [CleanText, NormalizeDuration],
    "ChargesAnnuelles": [CleanAmount, NormalizeAmount],
    "ChargesTrimestrielles": [CleanAmount, NormalizeAmount],
}

Reducers = {
    "Bailleur": FuzzyDeduplicate,
    "Preneur": FuzzyDeduplicate,
    "Adresse": FuzzyDeduplicate,
    "Dated'Effet": [Deduplicate, MostRecent],
    "DuréeTotale": Deduplicate,
    "DuréeFerme": Deduplicate,
    "MontantduLoyer": Deduplicate,
    "DépôtdeGarantie": Deduplicate,
    "Franchise": Deduplicate,
    "Indexation": Deduplicate,
    "Preavis": [Deduplicate, GreaterThan30],
    "ChargesAnnuelles": Deduplicate,
    "ChargesTrimestrielles": Deduplicate,
}


class MazarsTableProcessor(ProcessorBase):
    """Mazars normalizer."""

    def process(
        self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        params: MazarsTableParameters = cast(MazarsTableParameters, parameters)
        try:
            for document in documents:
                slots = []
                filtered_annotations = []
                for a in document.annotations:
                    if a.status != "KO" and a.labelName in Labels:
                        a.label = a.label or Labels.get(a.labelName)
                        if a.label in Normalizers.keys():
                            filtered_annotations.append(a)
                document.annotations = filtered_annotations
                ann_groups = group_annotations(document, by_label)
                for group, anns in ann_groups.items():
                    if group in Normalizers:
                        normalizer_fun = compose_functions(Normalizers[group])
                        for a in anns:
                            text = a.text or document.text[a.start:a.end]
                            a.properties = a.properties or {}
                            a.properties["normalized"] = normalizer_fun(text)
                ann_groups["Dated'Effet"] = ann_groups.pop(
                    "Dated'Effet (date)", None
                ) or ann_groups.pop("Dated'Effet (en lettre)", [])
                ann_groups["DépôtdeGarantie"] = ann_groups.pop("DépôtdeGarantie", [])
                if "DépôtdeGarantie (en lettre)" in ann_groups:
                    ann_groups["DépôtdeGarantie"].extend(
                        ann_groups.pop("DépôtdeGarantie (en lettre)")
                    )
                ann_groups["Franchise"] = ann_groups.pop(
                    "Franchise (en mois)", None
                ) or ann_groups.pop("Franchise (chiffre)", [])
                for col, reducers in Reducers.items():
                    reducer_fun = compose_functions(reducers)
                    anns = ann_groups.get(col, [])
                    texts = [a.properties["normalized"] for a in anns]
                    dedups = reducer_fun(texts)
                    slots.append(f"{col} : {' | '.join(dedups)}")
                slot = "\n".join(slots)
                if params.as_altText is not None and len(params.as_altText):
                    document.altTexts = document.altTexts or []
                    altTexts = [
                        alt
                        for alt in document.altTexts
                        if alt.name != params.as_altText
                    ]
                    altTexts.append(AltText(name=params.as_altText, text=slot))
                    document.altTexts = altTexts
                else:
                    document.text = slot
                    document.annotations = None
                    document.sentences = None
        except BaseException as err:
            raise err
        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return MazarsTableParameters


def group_annotations(doc: Document, keyfunc):
    def get_sort_key(a: Annotation):
        return a.end - a.start, -a.start

    groups = defaultdict(list)
    for k, g in groupby(sorted(doc.annotations, key=keyfunc), keyfunc):
        sorted_group = sorted(g, key=get_sort_key, reverse=True)
        groups[k] = sorted_group
    return groups


def by_label(a: Annotation):
    return a.label
