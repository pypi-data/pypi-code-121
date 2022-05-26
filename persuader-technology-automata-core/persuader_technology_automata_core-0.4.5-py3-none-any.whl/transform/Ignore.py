from dataclasses import dataclass, field


@dataclass
class Ignore:
    ignore: bool = field(default=False, init=False, )
