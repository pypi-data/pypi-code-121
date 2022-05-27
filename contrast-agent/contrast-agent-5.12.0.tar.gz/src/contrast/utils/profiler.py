# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import cProfile
import uuid
from contrast.utils.decorators import fail_loudly


class Profiler(cProfile.Profile):
    def __init__(self, path):
        super().__init__()

        from contrast.agent.settings import Settings

        self.settings = Settings()
        self.path = path

    def __enter__(self):
        if self.settings.is_profiler_enabled:
            self.enable()
        return self

    def __exit__(self, *exc_info):
        if self.settings.is_profiler_enabled:
            self.disable()
            self.save_profile_data()

    @fail_loudly("Unable to save profile data")
    def save_profile_data(self):
        path = self.path.strip("/").replace("/", "-")
        self.dump_stats(f"{path}-{uuid.uuid4().hex}-profiler-stats.out")
