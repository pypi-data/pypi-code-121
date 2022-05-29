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
from collections import OrderedDict
import logging
import logging.handlers
import math
import sys
import textwrap

from turberfield.dialogue import __version__
from turberfield.dialogue.cli import add_casting_options
from turberfield.dialogue.cli import add_common_options
from turberfield.dialogue.cli import add_performance_options
from turberfield.dialogue.cli import resolve_objects
from turberfield.dialogue.matcher import Matcher
from turberfield.dialogue.model import Model
from turberfield.dialogue.performer import Performer
from turberfield.utils.logger import LogAdapter
from turberfield.utils.logger import LogManager

__doc__ = """
A utility to generate a printable screenplay.

The output is HTML. It is styled to be an input to WeasyPrint_, so you can ultimately
create a script in PDF format.

There are command line options to change the timing of dialogue, to repeat the action,
and to control the number of roles an entity may take.

Example (see the episode `Blue Monday`_)::

    turberfield-dialogue    --references=bluemonday78.logic:references
                            --folder=bluemonday78.logic:ray
                            --folder=bluemonday78.logic:justin
                            --folder=bluemonday78.logic:local
                            --roles=1
                            --repeat=0
                            --strict

.. _Blue Monday: https://github.com/tundish/blue_monday_78
.. _WeasyPrint: http://weasyprint.org/

"""

class HTMLHandler:


    @staticmethod
    def format_dialogue(shots, dwell, pause):
        pad = int(math.log10(sum(len(rows) for rows in shots.values()) + 1)) + 1
        return "\n".join(textwrap.dedent("""
            <section id="{id}">
            <table>
            <caption>
            <dl>
            <dt>Scene</dt>
            <dd>{shot.scene}</dd>
            <dt>Shot</dt>
            <dd>{shot.name}</dd>
            <dt>Duration</dt>
            <dd>{duration:.1f} s</dd>
            <dl>
            </caption>
            <thead>
            <tr>
            <th>Character</th>
            <th></th>
            <th>Notes</th>
            </tr>
            </thead>

            <tbody>
            {body}
            </tbody>
             <tfoot>
             <tr>
             <td></td>
             <td></td>
             <td><dl><dt>dwell</dt><dd>{dwell}</dd><dt>pause</dt><dd>{pause}</dd></dl></td>
             </tr>
             </tfoot>
            </table>
            </section>
        """).format(
            id=i + 1,
            shot=shot._replace(name=shot.name.capitalize(), scene=shot.scene.capitalize()),
            dwell=dwell,
            pause=pause,
            duration=sum(i[-1] for i in rows if i is not None),
            body="\n".join(
                ('<tr><td class="{cue}">{name}</td>\n'
                 '<td>{text}</td>\n<td>{notes}</td>\n</tr>').format(
                    cue="cue" if name != "" else "",
                    name=" ".join(i.capitalize() for i in name.split()) if name else "",
                    text="<strong>{0}</strong>".format(text) if name is None else text,
                    notes="{0:02.2f}s. {1:0{2}}".format(span, n + 1, pad)
                ) for n, (name, text, span) in enumerate(rows)
            )
        ) for i, (shot, rows) in enumerate(shots.items()) if shot)


    @staticmethod
    def format_metadata(**kwargs):
        return "<dl>\n{0}\n</dl>".format(
            "\n".join(
                "<dt>{0}</dt>\n{1}\n".format(
                    key.capitalize(),
                    "\n".join(
                        "<dd>{0}</dd>".format(val)
                        for val in sorted(kwargs[key])
                    )
                )
                for key in sorted(kwargs.keys())
            )
        )

    @staticmethod
    def format_summary(shots, default="?"):
        return "<ol>\n{0}\n</ol>".format(
            "\n".join(
                '<li><a href="#{0}">{1}</a></li>'.format(
                    i + 1,
                    default if not shot else shot.name.capitalize()
                )
                for i, (shot, rows) in enumerate(shots.items())
            )
        )

    def __init__(self, dwell, pause):
        self.dwell = dwell
        self.pause = pause
        self.speaker = None
        self.shot = None
        self.shots = OrderedDict()

    def __call__(self, obj):
        if isinstance(obj, Model.Line):
            yield self.handle_line(obj)
        elif isinstance(obj, Model.Shot):
            shot = obj._replace(items=None)
            if shot != self.shot:
                self.shots[shot] = []
                self.shot = shot
            yield obj
        else:
            yield obj

    def handle_line(self, obj):
        if obj.persona is None:
            return 0

        # TODO: Fix this properly in turberfield-dialogue
        text = obj.text.replace("   ", " ").replace("  ", " ")
        if self.speaker is not obj.persona:
            self.speaker = obj.persona
            try:
                name = "{0.firstname} {0.surname}".format(self.speaker.name).strip()
            except AttributeError:
                name = None
        else:
            name = ""

        span = self.pause + self.dwell * text.count(" ")
        self.shots.setdefault(self.shot, []).append((name, text, span))
        return obj

    def to_html(self, metadata, **kwargs):
        # https://www.w3.org/TR/css3-page/
        # https://developer.mozilla.org/en-US/docs/Web/CSS/%40page
        return textwrap.dedent("""
            <!doctype html>
            <html lang="en">
            <head>
            <meta charset="utf-8" />
            <title>Script</title>
            <style>
            @page {{
                size: A4;
                margin: 15mm 5mm 10mm 20mm;
                @top-center {{
                    content: counter(page) " / " counter(pages);
                    width: 100%;
                    vertical-align: bottom;
                    border-bottom: .5pt solid;
                    margin-bottom: .7cm;
                }}
            }}
            html {{
                font-family: 'helvetica neue', helvetica, arial, sans-serif;
            }}
            section {{
                break-before: page;
            }}
            table {{
              table-layout: fixed;
              width: 100%;
              border-collapse: collapse;
            }}

            thead th:nth-child(1) {{
              width: 10%;
            }}

            thead th:nth-child(2) {{
              width: 65%;
            }}

            thead th:nth-child(3) {{
              width: 20%;
            }}

            td.cue {{
              border-top: #c5c5c5 dotted 1px;
            }}

            tr td:nth-child(1) {{
              padding: 0.5em;
              padding-left: 0.1em;
              text-align: left;
            }}

            tr td:nth-child(2) {{
              padding: 1.5em;
            }}

            tr td:nth-child(3) {{
              font-size: 0.7em;
              padding: 0 0.5em 0.5em 0.5em;
              text-align: left;
              vertical-align: top;
            }}

            table caption {{
              break-after: avoid;
            }}

            td {{
              padding: 1em 0 1em 0;
              font-family: monospace;
            }}

            dt {{
            clear: left;
            color: olive;
            float: left;
            font-family: "monospace";
            padding-right: 0.3em;
            text-align: right;
            text-transform:capitalize;
            width: 100px;
            }}

            dt:after {{
            content: ":";
            }}

            </style>
            </head>
            <body>
            <h1>Script</h1>
            {metadata}
            {summary}
            {dialogue}
            </body>
            </html>
        """).format(
            metadata=self.format_metadata(**metadata),
            summary=self.format_summary(self.shots),
            dialogue=self.format_dialogue(self.shots, self.dwell, self.pause)
        ).lstrip()

def main(args):
    log_manager = LogManager()
    log = log_manager.get_logger("main")

    if args.log_path:
        log.set_route(args.log_level, LogAdapter(), sys.stderr)
        log.set_route(log.Level.NOTSET, LogAdapter(), args.log_path)
    else:
        log.set_route(args.log_level, LogAdapter(), sys.stderr)

    folders, references = resolve_objects(args)
    matcher = Matcher(folders)
    performer = Performer(folders, references)
    interlude = None
    handler = HTMLHandler(dwell=args.dwell, pause=args.pause)
    items = []
    folder = True
    log.info("Reading sources...")
    while folder and not performer.stopped:
        for i in range(args.repeat + 1):
            if performer.script:
                log.info("Script {0.fP}".format(performer.script))

            folder, index, script, selection, interlude = performer.next(
                folders, references, strict=args.strict, roles=args.roles
            )
            for item in performer.run(strict=args.strict, roles=args.roles):
                items.extend(list(handler(item)))

            if interlude is not None:
                metadata = interlude(folder, index, references)
                folder = next(matcher.options(metadata))

    log.info("Writing {0} items to output...".format(len(items)))
    print(handler.to_html(metadata=performer.metadata))
    log.info("Done.")
    return 0


def parser():
    return add_performance_options(
        add_casting_options(
            add_common_options(
                argparse.ArgumentParser(
                    __doc__,
                    fromfile_prefix_chars="@"
                )
            )
        )
    )

def run():
    p = parser()
    args = p.parse_args()
    if args.version:
        sys.stderr.write(__version__ + "\n")
        rv = 0
    else:
        rv = main(args)
    sys.exit(rv)

if __name__ == "__main__":
    run()
