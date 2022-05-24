CONLL_HEADER = "\t".join(
    [
        "id",  # 1
        "form",  # 2
        "lemma",  # 3
        "cpos",  # 4
        "pos",  # 5
        "feat",  # 6
        "head",  # 7
        "deprel",  # 8
        "phead",  # 9
        "pdeprel",  # 10
    ]
)


def format_conll_sentence(sentence, universal_deps=False, universal=False, empty="-"):
    if not isinstance(sentence, (list, tuple)):
        raise TypeError("sentence must be an instance of list or tuple")
    if not all(isinstance(token, dict) for token in sentence):
        raise TypeError("each token must be an instance of dict")
    lines = ["#" + CONLL_HEADER]
    for tokid, token in enumerate(sentence, start=1):
        tokid = str(tokid)
        form = token.get("form")
        lemma = token.get("ulemma" if universal else "lemma", empty)
        cpos = token.get("upos" if universal else "pos", empty)
        pos = cpos
        feats = token.get(
            "ufeats" if universal else "feats",
            token.get("uinfl" if universal else "infl", empty),
        )
        head = str(
            token.get("uparent" if universal or universal_deps else "parent", empty)
        )
        deprel = token.get(
            "udeprel" if universal or universal_deps else "deprel", empty
        )
        phead = head
        pdeprel = deprel

        lines.append(
            "\t".join(
                [
                    tokid,  # 1
                    form,  # 2
                    lemma,  # 3
                    cpos,  # 4
                    pos,  # 5
                    feats,  # 6
                    head,  # 7
                    deprel,  # 8
                    phead,  # 9
                    pdeprel,  # 10
                ]
            )
        )
    lines.append("")  # empty line marks end of sentence
    return "\n".join(lines) + "\n"  # end with newline
