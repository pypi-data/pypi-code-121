from typing import Optional

from sila2.framework.utils import xpath_sila


class NamedNode:
    _identifier: str
    _display_name: str
    _description: str

    def __init__(self, fdl_node):
        self._identifier = xpath_sila(fdl_node, "sila:Identifier")[0].text.strip()
        display_name: Optional[str] = xpath_sila(fdl_node, "sila:DisplayName")[0].text
        self._display_name = "" if display_name is None else display_name
        description: Optional[str] = xpath_sila(fdl_node, "sila:Description")[0].text
        self._description = "" if description is None else description
