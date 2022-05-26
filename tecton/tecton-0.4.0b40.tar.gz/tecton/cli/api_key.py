import sys

import click

import tecton
from tecton._internals import metadata_service
from tecton.cli import printer
from tecton.cli.command import TectonGroup
from tecton_proto.metadataservice.metadata_service_pb2 import CreateApiKeyRequest
from tecton_proto.metadataservice.metadata_service_pb2 import DeleteApiKeyRequest
from tecton_proto.metadataservice.metadata_service_pb2 import ListApiKeysRequest
from tecton_spark.id_helper import IdHelper


# TODO(fix the "readonly" part of this help string)
@click.command("api-key", cls=TectonGroup)
def api_key():
    """Interact with Tecton read-only API keys."""


@api_key.command()
@click.option("--description", default="", help="An optional, human readable description for this API key.")
@click.option(
    "--is-admin",
    is_flag=True,
    default=False,
    help="Whether the API key has admin permissions, generally corresponding to write permissions. Defaults to false.",
)
def create(description, is_admin):
    """Create a new API key."""
    request = CreateApiKeyRequest()
    request.description = description
    request.is_admin = is_admin
    response = metadata_service.instance().CreateApiKey(request)
    printer.safe_print("Save this key - you will not be able to get it again.", file=sys.stderr)
    printer.safe_print(response.key)


@api_key.command()
@click.argument("id", required=True)
def delete(id):
    """Deactivate an API key by its ID."""
    request = DeleteApiKeyRequest()
    try:
        id_proto = IdHelper.from_string(id)
    except:
        printer.safe_print(f"Invalid format for ID")
        sys.exit(1)
    request.id.CopyFrom(id_proto)
    try:
        response = metadata_service.instance().DeleteApiKey(request)
    except tecton._internals.tecton_errors.TectonAPIValidationError as e:
        printer.safe_print(
            f"API key with ID {id} not found. Check `tecton api-key list` to find the IDs of currently active API keys. The key's ID is different from the key's secret value."
        )
        sys.exit(1)
    printer.safe_print("Success")


@api_key.command()
def list():
    """List active API keys."""
    request = ListApiKeysRequest()
    response = metadata_service.instance().ListApiKeys(request)
    for k in response.api_keys:
        printer.safe_print(f"API Key ID: {IdHelper.to_string(k.id)}")
        printer.safe_print(f"Secret Key: {k.obscured_key}")
        printer.safe_print(f"Description: {k.description}")
        printer.safe_print(f"Created by:{k.created_by}")
        printer.safe_print()
