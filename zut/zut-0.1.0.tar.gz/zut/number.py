class PowerValue():
    def __init__(self, value, unit='B', base="decimal", maxrank=None):
        self.base = base
        if base == "binary":
            power = 1024
            self.rank_labels = []
            for rank in ['', 'Ki', 'Mi', 'Gi', 'Ti']:
                self.rank_labels.append(rank)
                if maxrank and rank != '' and maxrank.upper() == rank[0].upper():
                    break
        elif base == "decimal":
            power = 1000
            self.rank_labels = []
            for rank in ['', 'k', 'M', 'G', 'T']:
                self.rank_labels.append(rank)
                if maxrank and rank != '' and maxrank.upper() == rank[0].upper():
                    break
        else:
            raise ValueError(f'invalid base: {base}')

        self.unit = unit
        self.value = value
        self.rank = 0

        if self.value is None:
            return

        while self.value > power and self.rank < len(self.rank_labels) - 1:
            self.value /= power
            self.rank += 1
        
    def __str__(self):
        if self.value is None:
            return ''
        return ('{:,.1f}' if self.rank > 0 else '{:,.0f}').format(self.value) + ' ' + self.rank_labels[self.rank] + self.unit


def human_bytes(value, base="binary", maxrank=None):
    if value is None:
        return ''

    if base not in ["binary", "decimal", "both"]:
        raise ValueError("invalid base '%s'" % base)
        
    if base in ["binary", "both"]:
        binary_str = str(PowerValue(value, base="binary", maxrank=maxrank))
        if base == "binary":
            return binary_str

    if base in ["decimal", "both"]:
        decimal_str = str(PowerValue(value, base="decimal", maxrank=maxrank))
        if base == "decimal":
            return decimal_str
    
    if base == "both":
        return '%-12s' % binary_str + ' (' + decimal_str + ')'
