from typing import List
from dataclasses import dataclass
from mlplatform_lib.dataclass import DbSourceDataObjectCandidate


@dataclass
class DbSourceDataObjectCandidateList:
    db_source_data_object_candidate: List[DbSourceDataObjectCandidate]
