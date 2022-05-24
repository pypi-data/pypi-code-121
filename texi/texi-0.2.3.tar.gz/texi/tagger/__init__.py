# -*- coding: utf-8 -*-

from texi.tagger.sequence_labeling import IOB1, IOB2, IOBES, SequeceLabelingTagger

__all__ = [
    "sequence_labeling",
    "IOB1",
    "IOB2",
    "IOBES",
    "SequeceLabelingTagger",
]

taggers = {
    "iob1": IOB1,
    "iob2": IOB2,
    "iobes": IOBES,
}


def Tagger(scheme: str, *args, **kwargs):
    return taggers[scheme.lower()](*args, **kwargs)
