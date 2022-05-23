# Copyright 2020-2022 Daniel Harding
# Distributed as part of the pyflame project under the terms of the MIT license

import html

from django.template.loader import render_to_string

from debug_toolbar.panels import Panel

from pyflame.exceptions import MissingFlamegraphScript
from pyflame.render import stack_counts_to_svg
from pyflame.sampler import Sampler

from pyflame.djdt.settings import get_config


class FlamegraphPanel(Panel):
    title = 'Flamegraph'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sampler = None
        self.stack_counts = {}

    @property
    def content(self):
        config = get_config()
        try:
            svg = stack_counts_to_svg(
                self.stack_counts,
                config['FLAMEGRAPH_SCRIPT_PATH'],
                config['FLAMEGRAPH_SCRIPT_EXTRA_ARGS'],
            )
        except MissingFlamegraphScript:
            srcdoc = None
        else:
            srcdoc = html.escape(svg)
        return render_to_string('pyflame/panel.html', {'srcdoc': srcdoc})

    def enable_instrumentation(self):
        if self.sampler is None:
            self.sampler = Sampler(get_config()['SAMPLE_INTERVAL'])

    def disable_instrumentation(self):
        if self.sampler is not None:
            self.stack_counts = self.sampler.stop()
            self.sampler = None
