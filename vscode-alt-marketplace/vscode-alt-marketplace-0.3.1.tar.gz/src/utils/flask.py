import html
from io import StringIO
import mimetypes
from typing import Literal
from flask import Flask, Response, abort, request
from pathlib import Path

from markdown import markdown


def allow_cors(response: Response):
    origin = request.headers.get("Origin")
    if origin:
        response.headers.add("Access-Control-Allow-Origin", origin)
    # response.headers.add("Access-Control-Allow-Credentials", "true")
    if request.access_control_request_headers:
        response.access_control_allow_headers = request.access_control_request_headers
    if request.access_control_request_method:
        response.access_control_allow_methods = [request.access_control_request_method]
    return response


def load_ssl_context(path: str, sans: "list[str]"):
    host = sans[0]
    crt = Path(path)
    from ssl import SSLContext, PROTOCOL_TLS_SERVER
    from x509creds import X509Credentials, parse_sans, x509, Encoding

    if not crt.exists():

        creds = X509Credentials.create(
            host, extensions=[x509.SubjectAlternativeName(parse_sans(sans))]
        )
        crt.parent.mkdir(exist_ok=True, parents=True)
        crt.write_bytes(creds.dump(Encoding.PEM))

    context = SSLContext(PROTOCOL_TLS_SERVER)
   # context.server = T
    X509Credentials.load(crt).apply_to_sslcontext(context)
    return context


_MIMETYPE = mimetypes.MimeTypes(strict=False)
_MIMETYPE.readfp(
    StringIO(
        """
application/vsix				vsix
text/markdown                     md
"""
    )
)


def render_as_html(data: bytes, mimetype: str = None):
    if data is None:
        return ""

    if mimetype is None or mimetype.startswith("text/"):
        text = data.decode()
        if mimetype in ["text/markdown", "text/x-markdown"]:
            return markdown(text)
        elif mimetype == "text/html":
            return text
        else:
            return f"<pre>{html.escape(text)}</pre>"
    else:
        return ""


def render_asset(data: bytes, filename: str):
    return render_as_html(data, _MIMETYPE.guess_type(filename)[0])


def return_asset(
    data: bytes,
    filename: str,
    disposition: Literal["inline", "attachment"] = "inline",
    mimetype: str = None,
):
    if data is None:
        abort(404)

    headers = {}
    if filename:
        headers[
            "Content-Disposition"
        ] = f"{disposition}; filename={filename}; filename*=utf-8''{filename}"
        if not mimetype:
            mimetype = _MIMETYPE.guess_type(filename)[0]

    return Response(data, mimetype=mimetype, headers=headers)


def debug_run(
    app: Flask,
    cert: str = "./.private/marketplace.visualstudio.com.crt",
    listen="127.0.0.1",
    sans=["marketplace.visualstudio.com", "vscode-gallery.local"],
):
    app.after_request(allow_cors)
    context = load_ssl_context(
        cert,
        [listen, *sans],
    )
    app.run(
        host=listen,
        port=443,
        ssl_context=context,
    )
