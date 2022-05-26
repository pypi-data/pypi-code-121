"""metrics commands for cmem command line interface."""
from typing import Tuple

import click

from prometheus_client import Metric

from cmem.cmemc.cli import completion
from cmem.cmemc.cli.commands import CmemcCommand, CmemcGroup
from cmem.cmemc.cli.utils import (
    metric_get_labels,
    metrics_get_dict,
    metrics_get_family,
    struct_to_table
)


def _filter_samples(family: Metric, label_filter: Tuple[str, str]) -> list:
    """Filter samples by labels."""
    all_samples = family.samples
    if not label_filter:
        return all_samples
    labels = metric_get_labels(family)
    samples = []
    for sample in all_samples:
        matching_labels = 0
        for name, value in label_filter:
            if name not in labels:
                raise ValueError(
                    f"The metric '{family.name}' does "
                    f"not have a label named '{name}'."
                )
            if value not in labels[name]:
                raise ValueError(
                    f"The metric '{family.name}' does "
                    f"not have a label '{name}' with the value '{value}'."
                )
            if name in sample.labels and sample.labels[name] == value:
                matching_labels += 1
        if matching_labels == len(label_filter):
            # all filter match
            samples.append(sample)
    return samples


# pylint: disable-msg=too-many-arguments
@click.command(cls=CmemcCommand, name="get")
@click.argument(
    "metric_id",
    required=True,
    type=click.STRING,
    autocompletion=completion.metric_ids
)
@click.option(
    "--job", "job_id",
    type=click.Choice(["DP"]),
    default="DP",
    show_default=True,
    help="The job from which the metrics data is fetched."
)
@click.option(
    "--filter", "label_filter",
    type=(str, str),
    autocompletion=completion.metric_label_filter,
    multiple=True,
    help="A set of label name/value pairs in order to filter the samples "
         "of the requested metric family. Each metric has a different set "
         "of labels with different values. "
         "In order to get a list of possible label names and values, use "
         "the command without this option. The label names are then shown "
         "as column headers and label values as cell values of this column."
)
@click.option(
    "--enforce-table",
    is_flag=True,
    help="A single sample value will be returned as plain text instead "
         "of the normal table. This allows for more easy integration "
         "with scripts. This flag enforces the use of tabular output, "
         "even for single row tables."
)
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw prometheus sample classes."
)
@click.pass_obj
def get_command(app, metric_id, job_id, label_filter, raw, enforce_table):
    """Get sample data of a metric.

    A metric of a specific job is identified by a metric ID. Possible
    metric IDs of a job can be retrieved with the `metrics list`
    command. A metric can contain multiple samples.
    These samples are distinguished by labels (name and value).
    """
    family = metrics_get_family(job_id, metric_id)
    samples = _filter_samples(family, label_filter)
    if len(samples) == 0:
        raise ValueError(
            "No data - the given label combination filtered out "
            f"all available samples of the metric {metric_id}."
        )

    if raw:
        for sample in samples:
            app.echo_info(str(sample))
        return

    if len(samples) == 1 and enforce_table is not True:
        app.echo_info(str(samples[0].value))
        return

    if family.type == "histogram":
        raise NotImplementedError(
            "Visualization of histogram metrics is not supported yet.\n"
            "Please use the 'metrics inspect' command to get the raw data."
        )

    label_dict = metric_get_labels(family, clean=True)
    table = []
    for sample in samples:
        row = []
        for key in sorted(label_dict.keys()):
            row.append(sample.labels[key])
        table.append(row)
        row.append(str(sample.value))
    headers = list(sorted(label_dict.keys()))
    headers.append("value")
    app.echo_info_table(
        table,
        headers=headers,
        sort_column=0
    )


@click.command(cls=CmemcCommand, name="inspect")
@click.argument(
    "metric_id",
    required=True,
    type=click.STRING,
    autocompletion=completion.metric_ids
)
@click.option(
    "--job", "job_id",
    type=click.Choice(["DP"]),
    default="DP",
    show_default=True,
    help="The job from which the metrics data is fetched."
)
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs raw JSON of the table data."
)
@click.pass_obj
def inspect_command(app, metric_id, job_id, raw):
    """Inspect a metric.

    This command outputs the data of a metric.
    The first table includes basic meta data about the metric.
    The second table includes sample labels and values.
    """
    family = metrics_get_family(job_id, metric_id)
    if raw:
        app.echo_info_json(
            {
                "family": family.__dict__,
                "labels": metric_get_labels(family)
            }
        )
        return
    app.echo_info_table(
        struct_to_table(family.__dict__),
        headers=["Key", "Value"],
        sort_column=0
    )
    app.echo_info_table(
        struct_to_table(metric_get_labels(family)),
        headers=["Label", "Value"],
        sort_column=0
    )


@click.command(cls=CmemcCommand, name="list")
@click.option(
    "--job", "job_id",
    type=click.Choice(["DP"]),
    default="DP",
    show_default=True,
    help="The job from which the metrics data is fetched."
)
@click.option(
    "--id-only",
    is_flag=True,
    help="Lists metric identifier only. "
         "This is useful for piping the IDs into other commands."
)
@click.option(
    "--raw",
    is_flag=True,
    help="Outputs (sorted) JSON dict, parsed from the metrics API output."
)
@click.pass_obj
def list_command(app, job_id, id_only, raw):
    """List metrics for a specific job.

    For each metric, the output table shows the metric ID,
    the type of the metric, a count of how many labels (label names)
    are describing the samples (L) and a count of how many samples are
    currently available for a metric (S).
    """
    data = metrics_get_dict(job_id=job_id)
    if raw:
        output = {}
        for key, family in sorted(data.items()):
            output[key] = family.__dict__
        app.echo_info_json(output)
        return
    if id_only:
        for key, family in sorted(data.items()):
            app.echo_info(key)
        return

    table = []
    for key, family in sorted(data.items()):
        labels = metric_get_labels(family)
        table.append([
            family.name,
            family.type,
            len(labels),
            len(family.samples)
        ])

    app.echo_info_table(
        table,
        headers=["ID", "Type", "L", "S"],
        sort_column=0
    )


@click.group(cls=CmemcGroup)
def metrics():
    """List and get metrics.

    This command group consists of commands for reading and listing
    internal monitoring metrics of eccenca Corporate Memory. A
    deployment consists of multiple jobs (e.g. DP, DI), which provide
    multiple metric families on an endpoint.

    Each metric family can consist of different samples identified by
    labels with a name and a value (dimensions). A metric has a specific
    type (counter, gauge, summary and histogram) and additional metadata.

    Please have a look at https://prometheus.io/docs/concepts/data_model/
    for further details.
    """


metrics.add_command(get_command)
metrics.add_command(inspect_command)
metrics.add_command(list_command)
