# -*- coding: utf-8 -*-

from typing import Any, Dict, Iterable, Optional

from kiara import KiaraModule
from kiara.exceptions import KiaraProcessingException
from kiara.models.module import KiaraModuleConfig
from kiara.models.values.value import ValueMap
from kiara.modules import ValueSetSchema
from kiara_plugin.core_types.models import ListModel
from kiara_plugin.tabular.models.table import KiaraArray
from pydantic import Field


def get_stopwords():

    # TODO: make that smarter
    pass

    import nltk

    nltk.download("punkt")
    nltk.download("stopwords")
    from nltk.corpus import stopwords

    return stopwords


class TokenizeTextConfig(KiaraModuleConfig):

    filter_non_alpha: bool = Field(
        description="Whether to filter out non alpha tokens.", default=True
    )
    min_token_length: int = Field(description="The minimum token length.", default=3)
    to_lowercase: bool = Field(
        description="Whether to lowercase the tokens.", default=True
    )


class TokenizeTextModule(KiaraModule):
    """Tokenize a string."""

    _config_cls = TokenizeTextConfig
    _module_type_name = "tokenize.string"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        inputs = {"text": {"type": "string", "doc": "The text to tokenize."}}

        return inputs

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        outputs = {
            "token_list": {
                "type": "list",
                "doc": "The tokenized version of the input text.",
            }
        }
        return outputs

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        import nltk

        # TODO: module-independent caching?
        # language = inputs.get_value_data("language")
        #
        text = inputs.get_value_data("text")
        tokenized = nltk.word_tokenize(text)

        result = tokenized
        if self.get_config_value("min_token_length") > 0:
            result = (
                x
                for x in tokenized
                if len(x) >= self.get_config_value("min_token_length")
            )

        if self.get_config_value("filter_non_alpha"):
            result = (x for x in result if x.isalpha())

        if self.get_config_value("to_lowercase"):
            result = (x.lower() for x in result)

        outputs.set_value("token_list", list(result))


class TokenizeTextArrayeModule(KiaraModule):
    """Split sentences into words or words into characters.
    In other words, this operation establishes the word boundaries (i.e., tokens) a very helpful way of finding patterns. It is also the typical step prior to stemming and lemmatization
    """

    _module_type_name = "tokenize.texts_array"

    KIARA_METADATA = {
        "tags": ["tokenize", "tokens"],
    }

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "texts_array": {
                "type": "array",
                "doc": "An array of text items to be tokenized.",
            },
            "tokenize_by_word": {
                "type": "boolean",
                "doc": "Whether to tokenize by word (default), or character.",
                "default": True,
            },
        }

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "tokens_array": {
                "type": "array",
                "doc": "The tokenized content, as an array of lists of strings.",
            }
        }

    def process(self, inputs: ValueMap, outputs: ValueMap):

        import warnings

        import nltk
        import numpy as np
        import pyarrow as pa
        import vaex

        array: KiaraArray = inputs.get_value_data("texts_array")
        # tokenize_by_word: bool = inputs.get_value_data("tokenize_by_word")

        column: pa.Array = array.arrow_array

        warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)

        def word_tokenize(word):
            result = nltk.word_tokenize(word)
            return result

        df = vaex.from_arrays(column=column)

        tokenized = df.apply(word_tokenize, arguments=[df.column])

        result_array = tokenized.to_arrow(convert_to_native=True)
        # TODO: remove this cast once the array data type can handle non-chunked arrays
        chunked = pa.chunked_array(result_array)
        outputs.set_values(tokens_array=chunked)

        # pandas_series: Series = column.to_pandas()
        #
        # tokenized = pandas_series.apply(lambda x: nltk.word_tokenize(x))
        #
        # result_array = pa.Array.from_pandas(tokenized)
        #
        # outputs.set_values(tokens_array=result_array)


class AssembleStopwordsModule(KiaraModule):
    """Create a list of stopwords from one or multiple sources.

    This will download nltk stopwords if necessary, and merge all input lists into a single, sorted list without duplicates.
    """

    _module_type_name = "create.stopwords_list"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "languages": {
                "type": "list",
                "doc": "A list of languages, will be used to retrieve language-specific stopword from nltk.",
                "optional": True,
            },
            "stopword_lists": {
                "type": "list",
                "doc": "A list of lists of stopwords.",
                "optional": True,
            },
        }

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "stopwords_list": {
                "type": "list",
                "doc": "A sorted list of unique stopwords.",
            }
        }

    def process(self, inputs: ValueMap, outputs: ValueMap):

        stopwords = set()
        _languages = inputs.get_value_obj("languages")

        if _languages.is_set:
            all_stopwords = get_stopwords()
            languages: ListModel = _languages.data

            for language in languages.list_data:

                if language not in all_stopwords.fileids():
                    raise KiaraProcessingException(
                        f"Invalid language: {language}. Available: {', '.join(all_stopwords.fileids())}."
                    )
                stopwords.update(get_stopwords().words(language))

        _stopword_lists = inputs.get_value_obj("stopword_lists")
        if _stopword_lists.is_set:
            stopword_lists: ListModel = _stopword_lists.data
            for stopword_list in stopword_lists.list_data:
                if isinstance(stopword_list, str):
                    stopwords.add(stopword_list)
                else:
                    stopwords.update(stopword_list)

        outputs.set_value("stopwords_list", sorted(stopwords))


class RemoveStopwordsModule(KiaraModule):
    """Remove stopwords from an array of token-lists."""

    _module_type_name = "remove_stopwords.from.tokens_array"

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        # TODO: do something smart and check whether languages are already downloaded, if so, display selection in doc
        inputs: Dict[str, Dict[str, Any]] = {
            "tokens_array": {
                "type": "array",
                "doc": "An array of string lists (a list of tokens).",
            },
            "languages": {
                "type": "list",
                # "doc": f"A list of language names to use default stopword lists for. Available: {', '.join(get_stopwords().fileids())}.",
                "doc": "A list of language names to use default stopword lists for.",
                "optional": True,
            },
            "additional_stopwords": {
                "type": "list",
                "doc": "A list of additional, custom stopwords.",
                "optional": True,
            },
        }
        return inputs

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        outputs = {
            "tokens_array": {
                "type": "array",
                "doc": "An array of string lists, with the stopwords removed.",
            }
        }
        return outputs

    def process(self, inputs: ValueMap, outputs: ValueMap) -> None:

        import pyarrow as pa

        custom_stopwords = inputs.get_value_data("additional_stopwords")

        if inputs.get_value_obj("languages").is_set:
            _languages: ListModel = inputs.get_value_data("languages")
            languages = _languages.list_data
        else:
            languages = []

        stopwords = set()
        if languages:
            for language in languages:
                if language not in get_stopwords().fileids():
                    raise KiaraProcessingException(
                        f"Invalid language: {language}. Available: {', '.join(get_stopwords().fileids())}."
                    )
                stopwords.update(get_stopwords().words(language))

        if custom_stopwords:
            stopwords.update(custom_stopwords)

        orig_array = inputs.get_value_obj("tokens_array")  # type: ignore

        if not stopwords:
            outputs.set_value("tokens_array", orig_array)
            return

        # if hasattr(orig_array, "to_pylist"):
        #     token_lists = orig_array.to_pylist()

        tokens_array = orig_array.data.arrow_array

        # TODO: use vaex for this
        result = []
        for token_list in tokens_array:

            cleaned_list = [x for x in token_list.as_py() if x.lower() not in stopwords]
            result.append(cleaned_list)

        outputs.set_value("tokens_array", pa.chunked_array(pa.array(result)))


class PreprocessModule(KiaraModule):
    """Preprocess lists of tokens, incl. lowercasing, remove special characers, etc.

    Lowercasing: Lowercase the words. This operation is a double-edged sword. It can be effective at yielding potentially better results in the case of relatively small datasets or datatsets with a high percentage of OCR mistakes. For instance, if lowercasing is not performed, the algorithm will treat USA, Usa, usa, UsA, uSA, etc. as distinct tokens, even though they may all refer to the same entity. On the other hand, if the dataset does not contain such OCR mistakes, then it may become difficult to distinguish between homonyms and make interpreting the topics much harder.

    Removing stopwords and words with less than three characters: Remove low information words. These are typically words such as articles, pronouns, prepositions, conjunctions, etc. which are not semantically salient. There are numerous stopword lists available for many, though not all, languages which can be easily adapted to the individual researcher's needs. Removing words with less than three characters may additionally remove many OCR mistakes. Both these operations have the dual advantage of yielding more reliable results while reducing the size of the dataset, thus in turn reducing the required processing power. This step can therefore hardly be considered optional in TM.

    Noise removal: Remove elements such as punctuation marks, special characters, numbers, html formatting, etc. This operation is again concerned with removing elements that may not be relevant to the text analysis and in fact interfere with it. Depending on the dataset and research question, this operation can become essential.
    """

    _module_type_name = "preprocess.tokens_array"

    KIARA_METADATA = {
        "tags": ["tokens", "preprocess"],
    }

    def create_inputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "tokens_array": {
                "type": "array",
                "doc": "The tokens array to pre-process.",
            },
            "to_lowercase": {
                "type": "boolean",
                "doc": "Apply lowercasing to the text.",
                "default": False,
            },
            "remove_alphanumeric": {
                "type": "boolean",
                "doc": "Remove all tokens that include numbers (e.g. ex1ample).",
                "default": False,
            },
            "remove_non_alpha": {
                "type": "boolean",
                "doc": "Remove all tokens that include punctuation and numbers (e.g. ex1a.mple).",
                "default": False,
            },
            "remove_all_numeric": {
                "type": "boolean",
                "doc": "Remove all tokens that contain numbers only (e.g. 876).",
                "default": False,
            },
            "remove_short_tokens": {
                "type": "integer",
                "doc": "Remove tokens shorter than a certain length. If value is <= 0, no filtering will be done.",
                "default": False,
            },
            "remove_stopwords": {
                "type": "list",
                "doc": "Remove stopwords.",
                "optional": True,
            },
        }

    def create_outputs_schema(
        self,
    ) -> ValueSetSchema:

        return {
            "tokens_array": {
                "type": "array",
                "doc": "The pre-processed content, as an array of lists of strings.",
            }
        }

    def process(self, inputs: ValueMap, outputs: ValueMap):

        import pyarrow as pa
        import vaex

        tokens_array: KiaraArray = inputs.get_value_data("tokens_array")
        lowercase: bool = inputs.get_value_data("to_lowercase")
        remove_alphanumeric: bool = inputs.get_value_data("remove_alphanumeric")
        remove_non_alpha: bool = inputs.get_value_data("remove_non_alpha")
        remove_all_numeric: bool = inputs.get_value_data("remove_all_numeric")
        remove_short_tokens: int = inputs.get_value_data("remove_short_tokens")

        _remove_stopwords = inputs.get_value_obj("remove_stopwords")
        if _remove_stopwords.is_set:
            stopword_list: Optional[Iterable[str]] = _remove_stopwords.data.list_data
        else:
            stopword_list = None

        # it's better to have one method every token goes through, then do every test seperately for the token list
        # because that way each token only needs to be touched once (which is more effective)
        def check_token(token: str) -> Optional[str]:

            # remove short tokens first, since we can save ourselves all the other checks (which are more expensive)
            if remove_short_tokens > 0:
                if len(token) <= remove_short_tokens:
                    return None

            _token: str = token
            if lowercase:
                _token = _token.lower()

            if remove_non_alpha:
                match = _token if _token.isalpha() else None
                if match is None:
                    return None

            # if remove_non_alpha was set, we don't need to worry about tokens that include numbers, since they are already filtered out
            if remove_alphanumeric and not remove_non_alpha:
                match = _token if _token.isalnum() else None
                if match is None:
                    return None

            # all-number tokens are already filtered out if the remove_non_alpha methods above ran
            if remove_all_numeric and not remove_non_alpha:
                match = None if _token.isdigit() else _token
                if match is None:
                    return None

            if stopword_list and _token and _token.lower() in stopword_list:
                return None

            return _token

        df = vaex.from_arrays(column=tokens_array.arrow_array)

        processed = df.apply(
            lambda token_list: [
                x for x in (check_token(token) for token in token_list) if x is not None
            ],
            arguments=[df.column],
        )
        result_array = processed.to_arrow(convert_to_native=True)
        # TODO: remove this cast once the array data type can handle non-chunked arrays
        chunked = pa.chunked_array(result_array)

        outputs.set_values(tokens_array=chunked)
