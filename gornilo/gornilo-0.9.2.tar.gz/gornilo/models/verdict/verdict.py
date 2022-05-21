from gornilo.models.verdict.verdict_codes import *
from gornilo.models.verdict.api_constants import *
import json


# noinspection PyPep8Naming
class Verdict:
    def __init__(self, code: int, public_message: str = ''):
        self._code: int = code
        self._public_message: str = public_message

    @staticmethod
    def OK_WITH_FLAG_ID(public_flag_id: str, flag_id: str):
        return Verdict(OK, json.dumps({PUBLIC_FLAG_ID: public_flag_id, PRIVATE_CONTENT: flag_id}))

    @staticmethod
    def OK(flag_id: str = ''):
        return Verdict(OK, flag_id)

    @staticmethod
    def CORRUPT(public_reason: str):
        return Verdict(CORRUPT, public_reason)

    @staticmethod
    def MUMBLE(public_reason: str):
        return Verdict(MUMBLE, public_reason)

    @staticmethod
    def DOWN(public_reason: str):
        return Verdict(DOWN, public_reason)

    @staticmethod
    def CHECKER_ERROR(public_reason: str):
        return Verdict(CHECKER_ERROR, public_reason)
