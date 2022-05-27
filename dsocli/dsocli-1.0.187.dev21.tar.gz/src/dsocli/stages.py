
import re
from .constants import *
from .exceptions import DSOException


key_regex_pattern = r"^([a-zA-Z][a-zA-Z0-9_-]+)/?([0-9])?$"

class StageService():

    # @staticmethod
    # def default_stage():
    #     return 'default/0'

    def raw_parse(self, stage):
        if not stage:
            import traceback
            traceback.print_stack() 
            raise DSOException(MESSAGES['Stage'].format(stage, key_regex_pattern))
        m = re.match(key_regex_pattern, stage)
        if m is None:
            raise DSOException(MESSAGES['InvalidStage'].format(stage, key_regex_pattern))
        stage = m.groups()[0]
        env = int(m.groups()[1]) if len(m.groups()) > 1 and m.groups()[1] else ''
        return stage, env

    def normalize(self, value):
        stage, env = Stages.raw_parse(value)
        # stage = stage or 'default'
        ### force dafault env if stage is default: default/env not allowed
        env = env if env and not stage == self.short_default_stage else 0
        return f"{stage}/{env}"

    def parse_normalized(self, stage):
        stage = Stages.normalize(stage)
        return Stages.raw_parse(stage)

    def get_default_env(self, stage):
        stage = Stages.parse_normalized(stage)[0]
        return f"{stage}/0"

    def parse_name(self, stage):
        return Stages.parse_normalized(stage)[0]

    def parse_env(self, stage):
        return Stages.parse_normalized(stage)[1]

    def shorten(self, stage):
        if not stage: return self.short_default_stage
        stage, env = Stages.parse_normalized(stage)
        if env == 0:
            return f"{stage}"
        else:
            return f"{stage}/{env}"

    @property
    def default_stage(self):
        return 'default/0'

    @property
    def short_default_stage(self):
        return 'default'

    def is_default(self, stage):
        return stage in [self.default_stage, self.short_default_stage]

    def is_default_env(self, stage):
        env = Stages.parse_normalized(stage)[1]
        return env == 0


Stages = StageService()