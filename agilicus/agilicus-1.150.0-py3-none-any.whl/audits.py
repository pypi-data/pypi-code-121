from . import context
from . import input_helpers

from .input_helpers import strip_none
from .output import table
from .output.table import (
    column,
    subtable,
    format_table,
)


def query(ctx, **kwargs):
    token = context.get_token(ctx)
    apiclient = context.get_apiclient(ctx, token)
    kwargs["org_id"] = input_helpers.get_org_from_input_or_ctx(ctx, **kwargs)
    dt_from = kwargs.pop("dt_from", "now-1day")
    kwargs = strip_none(kwargs)

    query_results = apiclient.audits_api.list_audits(dt_from=dt_from, **kwargs)

    if query_results:
        return query_results.audits

    return []


def format_audit_list_as_text(ctx, audits, show_columns):
    attribute_columns = [
        column("attribute_type"),
        column("attribute_id"),
        column("attribute_org_id"),
    ]
    columns = []
    if not show_columns:
        columns = [
            column("time"),
            column("action"),
            column("user_id"),
            column("org_id"),
            column("source_ip"),
            column("target_resource_type"),
            column("target_id"),
            column("date", optional=True),
            column("trace_id"),
            column("session"),
            column("secondary_id"),
            column("tertiary_id"),
            column("parent_id"),
            column("grandparent_id"),
            subtable(ctx, "audit_attributes", attribute_columns),
        ]
    else:
        for col in show_columns:
            if col == "audit_attributes":
                columns.append(subtable(ctx, "audit_attributes", attribute_columns))
            else:
                columns.append(column(col))

    return format_table(ctx, audits, columns)

    for record in audits:
        date = "---"
        if record.time:
            date = record.time.strftime("%Y-%m-%d %H:%M:%S %z")

        table.add_row(
            [
                record.action,
                record.user_id,
                record.org_id,
                record.source_ip,
                record.target_resource_type,
                record.target_id,
                date,
                record.trace_id,
                record.session,
                record.secondary_id,
                record.tertiary_id,
                record.parent_id,
                record.grandparent_id,
            ]
        )
    table.align = "l"
    return table


def query_auth_audits(ctx, **kwargs):
    apiclient = context.get_apiclient(ctx)
    kwargs["org_id"] = input_helpers.get_org_from_input_or_ctx(ctx, **kwargs)
    dt_from = kwargs.pop("dt_from", "now-1day")
    kwargs = strip_none(kwargs)

    query_results = apiclient.audits_api.list_auth_records(dt_from=dt_from, **kwargs)

    if query_results:
        return query_results.auth_audits

    return []


def format_auth_audit_list_as_text(ctx, records):
    columns = [
        table.mapped_column("time", "date"),
        table.column("event"),
        table.column("user_id"),
        table.column("org_id"),
        table.column("source_ip"),
        table.column("token_id"),
        table.column("trace_id"),
        table.column("session"),
        table.column("issuer"),
        table.column("client_id"),
        table.column("application_name"),
        table.column("upstream_user_id"),
        table.column("login_org_id"),
        table.column("upstream_idp"),
        table.column("stage"),
        table.column("user_agent"),
    ]
    return table.format_table(ctx, records, columns)
