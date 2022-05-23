# -*- coding: utf-8 -*-
import hashlib


def md5_key(chrom, start, end, ref, alt, assembly) -> str:
    """Generate a md5 key representing uniquely the variant

    Accepts:
        chrom(str): chromosome
        start(int): variant start
        end(int): variant end
        ref(str): references bases
        alt(str): alternative bases
        assembly(str) genome assembly (GRCh37 or GRCh38)

    Returns:
        md5_key(str): md5 unique key

    """
    hash = hashlib.md5()
    hash.update(
        (" ".join([chrom, str(start), str(end), str(ref), str(alt), assembly])).encode("utf-8")
    )
    md5_key = hash.hexdigest()
    return md5_key
