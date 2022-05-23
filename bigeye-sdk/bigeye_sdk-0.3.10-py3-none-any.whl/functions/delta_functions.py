from typing import List, Dict

from bigeye_sdk.generated.com.torodata.models.generated import ComparisonColumnMapping, ColumnApplicableMetricTypes, \
    TableApplicableMetricTypes


def infer_column_mappings(source_metric_types: TableApplicableMetricTypes,
                          target_metric_types: TableApplicableMetricTypes) -> List[ComparisonColumnMapping]:
    sct: Dict[str, ColumnApplicableMetricTypes] = {
        i.column.display_name.lower().replace('_', ''): i
        for i in source_metric_types.applicable_metric_types
    }

    tct: Dict[str, ColumnApplicableMetricTypes] = {
        i.column.display_name.lower().replace('_', ''): i
        for i in target_metric_types.applicable_metric_types
    }

    column_mappings: List[ComparisonColumnMapping] = [
        ComparisonColumnMapping(source_column=sct[k].column, target_column=tct[k].column,
                                metrics=sct[k].applicable_metric_types)
        for k in sct.keys() if k in tct
        if sct[k].applicable_metric_types == tct[k].applicable_metric_types
    ]

    return column_mappings
