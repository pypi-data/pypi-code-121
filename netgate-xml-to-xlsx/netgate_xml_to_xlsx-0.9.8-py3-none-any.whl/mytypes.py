from typing import NewType

import lxml  # nosec

Node = NewType("Node", lxml.etree._Element)
