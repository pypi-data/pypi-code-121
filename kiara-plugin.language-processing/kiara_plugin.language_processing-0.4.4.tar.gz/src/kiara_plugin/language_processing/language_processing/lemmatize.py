# -*- coding: utf-8 -*-
# from typing import Mapping, Union, Any
#
# from kiara import KiaraModule
# from kiara.models.values.value import ValueMap
# from kiara.modules import ValueSetSchema
#
#
# class LemmatizeTokensArrayModule(KiaraModule):
#     """Lemmatize an array of token lists.
#
#     Compared to using the ``lemmatize_tokens`` module in combination with ``map``, this is much faster, since it uses
#     a spacy [pipe](https://spacy.io/api/language#pipe) under the hood.
#     """
#
#     KIARA_METADATA = {
#         "tags": ["lemma", "tokens", "lemmatize"],
#     }
#
#     _module_type_name = "lemmatize_tokens_array"
#
#     def create_inputs_schema(
#         self,
#     ) -> ValueSetSchema:
#
#         inputs = {
#             "tokens_array": {"type": "array", "doc": "An array of lists of tokens."}
#         }
#         return inputs
#
#     def create_outputs_schema(
#         self,
#     ) -> ValueSetSchema:
#
#         outputs = {
#             "tokens_array": {
#                 "type": "array",
#                 "doc": "An array of lists of lemmatized tokens.",
#             }
#         }
#         return outputs
#
#     def process(self, inputs: ValueMap, outputs: ValueMap) -> None:
#
#         import pyarrow as pa
#         from spacy.tokens import Doc
#         from spacy.util import DummyTokenizer
#
#         tokens: pa.Array = inputs.get_value_data("tokens_array")
#
#         # it_core_news_sm = install_and_import_spacy_package("it-core-news-sm")
#         import it_core_news_sm
#         it_nlp = it_core_news_sm.load(disable=["tagger", "parser", "ner"])
#         # it_nlp = it_core_news_sm.load(disable=["tagger"])
#
#         use_pipe = False
#
#         if not use_pipe:
#
#             result = []
#             for t_list in tokens:
#                 t = []
#                 for w in t_list:
#                     w_lemma = [token.lemma_ for token in it_nlp(w.as_py())]
#                     t.append(w_lemma[0])
#                 result.append(t)
#
#         else:
#
#             class CustomTokenizer(DummyTokenizer):
#                 def __init__(self, vocab):
#                     self.vocab = vocab
#
#                 def __call__(self, words):
#                     return Doc(self.vocab, words=words)
#
#             it_nlp.tokenizer = CustomTokenizer(it_nlp.vocab)
#             result = []
#
#             for doc in it_nlp.pipe(
#                 tokens.to_pylist(),
#                 batch_size=32,
#                 n_process=3,
#                 disable=["parser", "ner", "tagger"],
#             ):
#                 result.append([tok.lemma_ for tok in doc])
#
#         print("FINISHED")
#         outputs.set_value("tokens_array", pa.array(result))
