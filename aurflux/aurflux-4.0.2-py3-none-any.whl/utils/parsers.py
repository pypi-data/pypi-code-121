from __future__ import annotations

import re
import typing as ty
from .. import errors

def find_mentions(message_content: str):
   matches = re.finditer(r"<?(@!|@|@&|#)?(\d{17,20})>?", message_content)
   return [int(x.group(2)) for x in matches]


def regex_parse(regex: re.Pattern, content: str, groups: ty.List[int]):
   match = regex.fullmatch(content)
   if not match:
      raise ValueError()
   group_tuple = match.groups()
   return [group_tuple[i] for i in groups]

