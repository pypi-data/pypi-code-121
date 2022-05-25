import abc
import enum
from typing import List

from bigeye_cli.model.github_report import GitHubReport
from bigeye_sdk.generated.com.torodata.models.generated import ComparisonMetricInfo, ComparisonMetricStatus, \
    PredefinedMetricName, ComparisonTableInfo


class VersionControlReportType(enum.Enum):
    GITHUB = GitHubReport


deltas_url = "https://app.bigeye.com/deltas"

# TODO: This can all be dynamically generated. If we want to allow users to provide the desired fields.
__delta_header = """|  metric_name   | source_column | target_column | source_value | target_value | difference |"""
__delta_alignment = """| :------------: | :-----------: | :-----------: | :----------: | :----------: | :--------: |"""
__delta_row = """|      {mn}       |      {s_col}       |      {t_col}       |        {sv} |        {tv} |      {diff} |"""
__group_header = """| metric_name | group_alerts | source_column | target_column |"""
__group_alignment = """| :------------: | :-----------: | :-----------: | :----------: |"""
__group_row = """|      {mn}       |      {alerts}       |      {s_col}       |        {t_col} |"""
__collapsed_section = \
    """
<details>
  <summary>Alerts Summary</summary>
  
{details}
</details>
    """


def __format_row(metric_name: PredefinedMetricName,
                 source_column: str,
                 target_column: str,
                 source_value: str,
                 target_value: str,
                 difference: str) -> str:
    return __delta_row.format(mn=metric_name.name,
                              s_col=source_column,
                              t_col=target_column,
                              sv=source_value,
                              tv=target_value,
                              diff=difference)


def __format_delta_table(cmis: List[ComparisonMetricInfo]) -> str:
    rows = '\n'.join(__format_row(
        cmi.comparison_metric_configuration.metric.predefined_metric.metric_name,
        cmi.comparison_metric_configuration.source_column_name,
        cmi.comparison_metric_configuration.target_column_name,
        '{0:.1f}'.format(cmi.source_value),
        '{0:.1f}'.format(cmi.target_value),
        '{0:.2f}%'.format(cmi.difference * 100)
    ) for cmi in cmis if cmi.status == ComparisonMetricStatus.COMPARISON_METRIC_STATUS_ALERT)

    table = f"{__delta_header}\n{__delta_alignment}\n{rows}"

    return __collapsed_section.format(details=table)


def _format_report(source_table: str, target_table: str, cti: ComparisonTableInfo):
    link = f"[View Full Delta in Bigeye]({deltas_url}/{cti.comparison_table_configuration.id})"
    schema_match = f"#### Source and Target schema match is {cti.schema_match}"
    table_names = f"Source Table: {source_table}\nTarget Table: {target_table}"
    failed_metric_ratio = f"{cti.failed_metric_count} of {cti.metric_count} metrics have failed"
    report = f"{table_names}\n{__format_delta_table(cti.comparison_metric_infos)}\n{failed_metric_ratio}"

    return f"{report}\n{schema_match}\n{link}"


def __formate_group_row(metric_name: str, alerts: str, source_column: str, target_column: str):
    return __group_row.format(mn=metric_name,
                              alerts=alerts,
                              s_col=source_column,
                              t_col=target_column)


def __format_group_table(cmis: List[ComparisonMetricInfo]):
    rows = '\n'.join([__formate_group_row(
        metric_name=cmi.comparison_metric_configuration.metric.predefined_metric.metric_name.name,
        alerts=f"{cmi.critical_group_count} alerting of {cmi.group_count} groups",
        source_column=cmi.comparison_metric_configuration.source_column_name,
        target_column=cmi.comparison_metric_configuration.target_column_name)
        for cmi in cmis
        if cmi.status == ComparisonMetricStatus.COMPARISON_METRIC_STATUS_ALERT])

    table = f"{__group_header}\n{__group_alignment}\n{rows}"
    return __collapsed_section.format(details=table)


def _format_group_report(source_table: str, target_table: str, cti: ComparisonTableInfo):
    title = "### Grouped Delta Summary"
    table_names = f"Source Table: {source_table}\nTarget Table: {target_table}"
    group_by_columns = "Grouped by: " + ", ".join(gb.source_column_name
                                                  for gb in cti.comparison_table_configuration.group_bys)
    table = "\n".join([__format_group_table(cti.comparison_metric_infos)])
    failed_metric_ratio = f"{cti.failed_metric_count} of {cti.metric_count} metrics have failed"
    link = f"[View Full Delta in Bigeye]({deltas_url}/{cti.comparison_table_configuration.id})"

    return f"{title}\n{table_names}\n\n{group_by_columns}\n{table}\n{failed_metric_ratio}\n{link}"


class VendorReport(abc.ABC):

    @abc.abstractmethod
    def publish(self, source_table_name: str, target_table_name: str, cti: ComparisonTableInfo):
        pass

    @abc.abstractmethod
    def publish_group_bys(self, source_table_name: str, target_table_name: str, cti: ComparisonTableInfo):
        pass

# This generated Markdown tables similar to the dimensional view in Bigeye.
# It would clutter the comment's section in VCS but may be useful elsewhere.

# __group_row = """|      {dims}             {mn}       |      {sv}       |      {tv}       |        {diff} |"""
# __dim_header = """|  {dim_x}   """
# __dim_align = """| :------------: """
# __dim_val = """      {dim_val}   |"""

# def _format_dim_row(dims: str, metric_name: str, source_value: float, target_value: float,
#                     difference: float) -> str:
#     return __group_row.format(dims=dims,
#                               mn=metric_name,
#                               sv=source_value,
#                               tv=target_value,
#                               diff='{0:.2f}%'.format(difference * 100))

# def _format_dim_header(group_bys: List[ColumnNamePair]):
#     dims_header = ''
#     dims_alignment = ''
#     for gb in group_bys:
#         dims_header += __dim_header.format(dim_x=gb.source_column_name)
#         dims_alignment += __dim_align
#     header = f"{dims_header}{__group_header}"
#     alignment = f"{dims_alignment}{__group_alignment}"
#     return f"{header}\n{alignment}"
#
#
# def _format_dims(dimensions: List[MetricGroupDimension]):
#     return ''.join([__dim_val.format(dim_val=dim.column_value) for dim in dimensions])
#
#
# def _format_group_table(metric_name: str, cmgs: List[ComparisonMetricGroup]):
#     return "\n".join([_format_dim_row(dims=_format_dims(cmg.dimensions),
#                                       metric_name=metric_name,
#                                       source_value=cmg.source_value,
#                                       target_value=cmg.target_value,
#                                       difference=cmg.difference)
#                       for cmg in cmgs if cmg.status == ComparisonMetricStatus.COMPARISON_METRIC_STATUS_ALERT])
#
#
# def _format_group_report(source_table: str, target_table: str, group_bys: List[ColumnNamePair],
#                          group_infos: dict[str, List[ComparisonMetricGroup]]):
#     table_names = f"###Source Table: {source_table}\n###Target Table: {target_table}"
#     group_by_columns = "####Grouped by: " + ", ".join(gb.source_column_name for gb in group_bys)
#     header = _format_dim_header(group_bys)
#     table = "\n".join([_format_group_table(mn, cmgs) for mn, cmgs in group_infos.items()])
#
#     return f"{table_names}\n\n{group_by_columns}\n{header}\n{table}"
