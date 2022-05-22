import enum


class McmtMethod(str, enum.Enum):
    vchain = "vchain"
    mcxvchain = "mcxvchain"
    recursive = "recursive"
    standard = "standard"
    standard_no_neg_ctrl = "standard_no_neg_ctrl"
