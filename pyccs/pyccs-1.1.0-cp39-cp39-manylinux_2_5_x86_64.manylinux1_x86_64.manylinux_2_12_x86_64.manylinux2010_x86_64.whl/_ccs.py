from .pyccs import ccs


def find_consensus(seq):
    segments_str, ccs_seq = ccs(to_bytes(seq.upper()))
    if len(ccs_seq) == 0: 
        return None, None

    return segments_str, ccs_seq


def to_bytes(bytes_or_str):
    """
    Return Instance of bytes
    """
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value