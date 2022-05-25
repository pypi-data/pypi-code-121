from typing import List, Union, Tuple

TextSamplesVar = List[List[str]]
NumSamplesListVar = List[List[int]]
LabelSamplesVar = Union[TextSamplesVar, List[str]]

ClassificationLabelVar = List[str]
MultiLabelClassificationLabelVar = Union[List[List[str]], List[Tuple[str]]]