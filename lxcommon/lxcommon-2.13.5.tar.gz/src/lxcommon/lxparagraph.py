from .cintilformat import (
    parse_cintil_paragraph,
    read_cintil_paragraphs,
    format_cintil_paragraph,
)
from .lxsentence import LxSentence


class LxParagraph(list):
    def __init__(self, *sentences, default_cintil_format_spec=None, par_id=None):
        if not all(isinstance(sentence, LxSentence) for sentence in sentences):
            raise TypeError("all sentences must be instances of LxSentence")
        super().__init__(sentences)
        self.default_cintil_format_spec = default_cintil_format_spec
        self.par_id = par_id

    def __repr__(self):
        sentences = ", ".join([repr(s) for s in self])
        return f"LxParagraph({sentences})"

    @staticmethod
    def from_primitive_types(paragraph, default_cintil_format_spec=None):
        "This method is useful when one needs to send/receive paragraphs via XML-RPC"
        if not isinstance(paragraph, list):
            raise TypeError("argument must be a list")
        return LxParagraph(
            *[
                LxSentence.from_primitive_types(
                    sentence, default_cintil_format_spec=default_cintil_format_spec
                )
                for sentence in paragraph
            ],
            default_cintil_format_spec=default_cintil_format_spec,
        )

    def to_primitive_types(self):
        "This method is useful when one needs to send/receive paragraphs via XML-RPC"
        return [sentence.to_primitive_types() for sentence in self]

    def to_plain_text(self, sentence_sep="\n"):
        if not isinstance(sentence_sep, str):
            raise TypeError("sentence_sep must be a string")
        return sentence_sep.join([sentence.to_plain_text() for sentence in self])

    @staticmethod
    def from_cintil(paragraph, format_spec):
        return LxParagraph.from_primitive_types(
            parse_cintil_paragraph(paragraph, format_spec),
            default_cintil_format_spec=format_spec,
        )

    def to_cintil(self, format_spec=None):
        if format_spec is None:
            if self.default_cintil_format_spec is None:
                raise ValueError(
                    "format_spec cannot be None "
                    "because self.default_cintil_format_spec is None"
                )
            format_spec = self.default_cintil_format_spec
        return format_cintil_paragraph(self.to_primitive_types(), format_spec)

    @staticmethod
    def read_cintil_paragraphs(input_file, format_spec):
        for paragraph in read_cintil_paragraphs(input_file, format_spec):
            yield LxParagraph.from_primitive_types(
                paragraph, default_cintil_format_spec=format_spec
            )

    def write_cintil(self, output_file, format_spec):
        print(self.to_cintil(format_spec), file=output_file)

    def to_conll(self, universal_deps=False, universal=False):
        if self.par_id is None:
            conll = ["# <p>\n"]
        else:
            conll = [f"# <p id={self.par_id!r}>\n"]
        for sentence in self:
            conll.append(
                sentence.to_conll(universal_deps=universal_deps, universal=universal)
            )
        return "".join(conll)

    def write_conll(self, output_file, universal_deps=False, universal=False):
        output_file.write(
            self.to_conll(universal_deps=universal_deps, universal=universal)
        )

    def to_ctrees(self):
        for sentence in self:
            yield getattr(sentence, "ctree", "")

    def write_ctrees(self, output_file):
        for ctree in self.to_ctrees():
            print(ctree, file=output_file)
        print(file=output_file)

    def to_conll_ctrees(self):
        for sentence in self:
            yield sentence.to_conll_ctree()

    def write_conll_ctrees(self, output_file):
        for conll_ctree in self.to_conll_ctrees():
            print(conll_ctree, end="\n\n", file=output_file)

    def copy(self):
        return LxParagraph(*[sentence.copy() for sentence in self])


__all__ = ["LxParagraph"]
