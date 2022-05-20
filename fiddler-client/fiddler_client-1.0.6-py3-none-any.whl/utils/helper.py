import re
from typing import Union

import pandas as pd

from ..core_objects import BatchPublishType


def infer_data_source(source: Union[str, pd.DataFrame]):
    """
    Attempts to infer the type of object based on type
    """
    if isinstance(source, pd.DataFrame):
        source_type = BatchPublishType.DATAFRAME
    elif isinstance(source, str):
        if re.match(r'((s3-|s3\.)?(.*)\.amazonaws\.com|^s3://)', source):
            source_type = BatchPublishType.AWS_S3
        elif re.match(r'((gs-|gs\.)?(.*)\.cloud.google\.com|^gs://)', source):
            source_type = BatchPublishType.GCP_STORAGE
        else:
            source_type = BatchPublishType.LOCAL_DISK
    else:
        raise ValueError('Unable to infer BatchPublishType')

    return source_type
