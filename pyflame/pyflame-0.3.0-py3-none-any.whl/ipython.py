# Copyright 2020-2022 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license

import html

from IPython.core.magic import Magics, cell_magic, magics_class
from IPython.display import HTML

from traitlets import Float, List, Unicode

from pyflame.exceptions import MissingFlamegraphScript
from pyflame.render import stack_counts_to_svg
from pyflame.sampler import Sampler


COMPILE_FILENAME = '<pyflame-ipython-cell>'


def _preprocess_stack(stack):
    stack_iter = iter(stack)
    for name, filename, firstlineno in stack_iter:
        if filename == COMPILE_FILENAME:
            break
    return list(stack_iter)


@magics_class
class PyFlameMagic(Magics):
    flamegraph_script_path = Unicode(
        None,
        allow_none=True,
        help="The path to the flamegraph.pl script.  The default value of None tells"
            " pyflame to search for flamegraph.pl using the PATH environment variable.",
    ).tag(config=True)

    flamegraph_script_extra_args = List(
        [],
        help="A list of extra command line arguments to pass when invoking"
            " flamegraph.pl.",
    ).tag(config=True)

    default_sample_interval = Float(
        0.001,
        help="The amount time the sampler thread will wait between capturing stack"
            " traces, in seconds.",
    ).tag(config=True)

    @cell_magic
    def pyflame(self, line, cell):
        code = self.shell.compile(
            self.shell.transform_ast(
                self.shell.compile.ast_parse(self.shell.transform_cell(cell))
            ),
            COMPILE_FILENAME,
            'exec',
        )
        ns = self.shell.user_ns
        sampler = Sampler(self.default_sample_interval)
        exec(code, ns)
        stack_counts = sampler.stop()

        try:
            svg = stack_counts_to_svg(
                stack_counts,
                self.flamegraph_script_path,
                self.flamegraph_script_extra_args,
                include_stack=lambda stack: any(
                    filename == COMPILE_FILENAME
                    for name, filename, firstlineno in stack
                ),
                preprocess_stack=_preprocess_stack,
            )
        except MissingFlamegraphScript:
            return HTML(
                '<p>'
                  'Could not locate the <a href="https://github.com/brendangregg/'
                  'FlameGraph/blob/master/flamegraph.pl">flamegraph.pl</a> script.'
                  ' Either copy flamegraph.pl to a location on your'
                  ' <code style="display: inline;">PATH</code>, or configure the path'
                  ' to the script by adding the following line to your'
                  ' ipython_config.py file:'
                '</p>'
                '<p><code>c.PyFlameMagic.flamegraph_script_path ='
                ' "<i>&lt;path to flamegraph.pl&gt;</i>"</code></p>'
            )
        else:
            srcdoc = html.escape(svg)
            return HTML(
                '<div style="resize: vertical; overflow: hidden;">'
                    f'<iframe srcdoc="{srcdoc}" style="height: 100%; width: 100%;">'
                '</div>'
            )


def load_ipython_extension(ipython):
    ipython.register_magics(PyFlameMagic)
