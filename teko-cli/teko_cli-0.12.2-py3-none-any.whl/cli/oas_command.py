import json, pyaml
import sys
import yaml
import typer
import urllib.request

from teko.helpers.clog import CLog
from teko.services.oas.oas_service import OasService
from teko.services.oas.parse.openapi3 import OpenAPI
from teko.services.oas.parse.openapi3.object_base import Map

app = typer.Typer()


@app.command(name="parse")
def oas_parser(
        file: str = typer.Argument(..., help='path to OAS file'),
   ):
    """
    """
    CLog.info("Parse spec file!")
    oas_srv = OasService()
    oas_srv.parse_file(file)


@app.command(name="diff")
def oas_diff(
        doc_spec: str = typer.Argument(..., help='The name of the design oas file'),
        code_spec: str = typer.Argument(..., help='The name of the real oas file'),
   ):
    """
    """
    CLog.info("OAS compare spec!")
    OasService.diff_oas(code_spec, doc_spec)








