#!/usr/bin/env python3
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import cgi
import cgitb
import http.server
import logging
import os
import platform
import sys
import textwrap
import time
import urllib.parse
import uuid
import webbrowser

from blessings import Terminal
import pkg_resources

from turberfield.dialogue import __version__
from turberfield.dialogue.cli import add_casting_options
from turberfield.dialogue.cli import add_common_options
from turberfield.dialogue.cli import add_performance_options
from turberfield.dialogue.cli import resolve_objects
from turberfield.dialogue.handlers import CGIHandler
from turberfield.dialogue.handlers import TerminalHandler
from turberfield.dialogue.model import Model
from turberfield.dialogue.player import rehearse
from turberfield.utils.assembly import Assembly
from turberfield.utils.logger import LogAdapter
from turberfield.utils.logger import LogManager

DFLT_PORT = 8080
DFLT_DB = ":memory:"

__doc__ = """
A utility to perform a folder of dramatic screenplay.

There are command line options to change the timing of dialogue,
to repeat the action, and to control the number of roles an
entity may take.

Example::

    turberfield-rehearse    --references=logic:references
                            --folder=logic:folder
                            --roles=16
                            --dwell=0.4
                            --pause=1.0
                            --db=action.sl3

"""


def yield_resources(obj, *args, **kwargs):
    if isinstance(obj, Model.Audio):
        path = pkg_resources.resource_filename(obj.package, obj.resource)
        pos = path.find("lib", len(sys.prefix))
        if pos != -1:
            yield path[pos:]

def cgi_consumer(args):
    folders, references = resolve_objects(args)
    Assembly.register(*(i if isinstance(i, type) else type(i) for i in references))

    resources = list(rehearse(
        folders, references, yield_resources, repeat=0, roles=args.roles, strict=args.strict
    ))
    links = "\n".join('<link ref="prefetch" href="/{0}">'.format(i) for i in resources)
    params = [(k, v) for k, v in vars(args).items() if k not in ("folder", "session")]
    params.append(("session", uuid.uuid4().hex))
    params.extend([("folder", i) for i in args.folder])
    opts = urllib.parse.urlencode(params)
    url = "http://localhost:{0}/{1}/turberfield-rehearse?{2}".format(
        args.port, args.locn, opts
    )
    rv = textwrap.dedent("""
        Content-type:text/html

        <!doctype html>
        <html lang="en">
        <head>
        <meta charset="utf-8" />
        <title>Rehearsal</title>
        {links}
        <style>
        #line {{
            font-family: "monospace";
        }}
        #line .persona::after {{
            content: ": ";
        }}
        #event {{
            font-style: italic;
        }}
        </style>
        </head>
        <body class="loading">
        <h1>...</h1>
        <blockquote id="line">
        <header class="persona"></header>
        <p class="data"></p>
        </blockquote>
        <audio id="cue"></audio>
        <span id="event"></span>
        <script>
            if (!!window.EventSource) {{
                var source = new EventSource("{url}");
            }} else {{
                alert("Your browser does not support Server-Sent Events.");
            }}

            source.addEventListener("audio", function(e) {{
                console.log(e);
                var audio = document.getElementById("cue");
                audio.setAttribute("src", e.data);
                audio.currentTime = 0;
                audio.play();
            }}, false);

            source.addEventListener("line", function(e) {{
                console.log(e);
                var event = document.getElementById("event");
                event.innerHTML = "";
                var obj = JSON.parse(e.data);
                var quote = document.getElementById("line");
                var speaker = quote.getElementsByClassName("persona")[0];
                var line = quote.getElementsByClassName("data")[0];

                speaker.innerHTML = obj.persona.name.firstname;
                speaker.innerHTML += " ";
                speaker.innerHTML += obj.persona.name.surname;
                line.innerHTML = obj.html;

            }}, false);

            source.addEventListener("memory", function(e) {{
                var obj = JSON.parse(e.data);
                var event = document.getElementById("event");
                event.innerHTML = obj.html;
            }}, false);

            source.addEventListener("property", function(e) {{
                var obj = JSON.parse(e.data);
                var event = document.getElementById("event");
                event.innerHTML = "<";
                event.innerHTML += obj.object._name;
                event.innerHTML += ">.";
                event.innerHTML += obj.attr;
                event.innerHTML += " = ";
                event.innerHTML += obj.val.name || obj.val;
            }}, false);

            source.addEventListener("open", function(e) {{
                console.log("Connection was opened.");
            }}, false);

            source.addEventListener("error", function(e) {{
                console.log("Error: connection lost.");
            }}, false);

        </script>
        </body>
        </html>
    """).format(links=links, url=url).lstrip()
    return rv

def cgi_producer(args, stream=None):
    log_manager = LogManager()
    log = log_manager.get_logger("turberfield")
    log.info(args)
    try:
        handler = CGIHandler(
            Terminal(stream=stream),
            None if args.db == "None" else args.db,
            float(args.pause),
            float(args.dwell)
        )
    except Exception as e:
        log.error(e)
        raise

    print("Content-type:text/event-stream", file=handler.terminal.stream)
    print(file=handler.terminal.stream)

    folders, references = resolve_objects(args)
    Assembly.register(*(i if isinstance(i, type) else type(i) for i in references))
    log.info(folders)
    try:
        yield from rehearse(
            folders, references, handler,
            int(args.repeat), int(args.roles),
            args.strict
        )
    except Exception as e:
        log.error(e)
        raise
    else:
        log.debug(references)

def presenter(args):
    handler = TerminalHandler(Terminal(), args.db, args.pause, args.dwell)
    folders, references = resolve_objects(args)
    Assembly.register(*(i if isinstance(i, type) else type(i) for i in references))

    if args.log_level != logging.DEBUG:
        with handler.terminal.fullscreen():
            for folder in folders:
                yield from rehearse(
                    folder, references, handler, args.repeat, args.roles, args.strict
                )
                input("Press return.")
    else:
        for folder in folders:
            yield from rehearse(
                folder, references, handler, args.repeat, args.roles, args.strict
            )

def main(args):
    log_manager = LogManager()
    log = log_manager.get_logger("main")

    if args.log_path:
        log.set_route(args.log_level, LogAdapter(), sys.stderr)
        log.set_route(log.Level.NOTSET, LogAdapter(), args.log_path)
    else:
        log.set_route(args.log_level, LogAdapter(), sys.stderr)

    if args.web:
        os.chdir(sys.prefix)
        log.warning("Web mode: running scripts from directory {0}".format(os.getcwd()))
        params = [
            (k, getattr(args, k))
            for k in (
                "log_level", "log_path", "port",
                "session", "locn", "references",
                "pause", "dwell", "repeat", "roles", "strict"
            )
        ]
        params.extend([("folder", i) for i in args.folder])
        log.info(params)
        opts = urllib.parse.urlencode(params)
        url = "http://localhost:{0}/{1}/turberfield-rehearse?{2}".format(
            args.port, args.locn, opts
        )
        log.info(url)
        webbrowser.open_new_tab(url)
        Handler = http.server.CGIHTTPRequestHandler
        Handler.cgi_directories = ["/{0}".format(args.locn)]
        httpd = http.server.HTTPServer(("", args.port), Handler)

        log.info("serving at port {0}".format(args.port))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            log.info("Shutdown.")
            return 0

    elif "SERVER_NAME" in os.environ:
        form = cgi.FieldStorage()
        params = {
            key: getattr(form[key], "value", form.getlist(key)) if key in form else None
            for key in vars(args).keys()
        }
        params["folder"] = form.getlist("folder")
        log_manager = LogManager()
        log = log_manager.get_logger("turberfield")
        log.info("params")
        log.info(params)
        cgitb.enable()
        args = argparse.Namespace(**params)
        if not args.session:
            log.info("Consumer view.")
            print(cgi_consumer(args))
        else:
            log.info("Producer view.")
            list(cgi_producer(args))
            while True:
                log.info("Sleeping...")
                time.sleep(3)
    else:
        for line in presenter(args):
            log.debug(line)
    return 0

def parser(description=__doc__):
    rv = add_performance_options(
        add_casting_options(
            add_common_options(
                argparse.ArgumentParser(
                    description,
                    fromfile_prefix_chars="@"
                )
            )
        )
    )
    rv.add_argument(
        "--web", action="store_true", default=False,
        help="Activate the web interface")
    rv.add_argument(
        "--db", required=False, default=None,
        help="Database URL.")
    rv.add_argument(
        "--session", required=False, default="",
        help="Session id (internal use only)")
    rv.add_argument(
        "--locn", required=False,
        default="Scripts" if "windows" in platform.system().lower() else "bin",
        help="Script location (internal use only)")
    rv.add_argument(
        "--port", type=int, default=DFLT_PORT,
        help="Set the port number of the web interface [{}]".format(DFLT_PORT))
    return rv

def run():
    p = parser()
    args = p.parse_args()

    rv = 0
    if args.version:
        sys.stdout.write(__version__)
        sys.stdout.write("\n")
    else:
        rv = main(args)

    if rv == 2:
        sys.stderr.write("\n Missing command.\n\n")
        p.print_help()

    sys.exit(rv)

if __name__ == "__main__":
    run()
