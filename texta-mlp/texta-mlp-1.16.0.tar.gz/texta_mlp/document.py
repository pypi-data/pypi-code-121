import math
from typing import List, Optional

import regex as re
import stanza
from lang_trans.arabic import buckwalter
from pelecanus import PelicanJson

from .entity_mapper import EntityMapper
from .fact import Fact
from .parsers import AddressParser, ContactEmailNamePairParser, ContactEmailParser, ContactPhoneParserHighPrecision, \
    ContactPhoneParserHighRecall, ContactPhoneParserStrict
from .russian_transliterator import Transliterate


russian_transliterator = Transliterate()


class Document:
    """
    Class for isolating the different values of MLP like pos_tags, lemmas etc
    and their formatting. For adding/changing the values, create a function with the name
    of the analyzer like "forms()" that handles populating the __forms attribute and a "get_forms()"
    function to format it. In the end add "get_forms()" to the to_json() function.
    """
    langs_to_transliterate = ["ru", "ar"]

    FACT_NAME_EMAIL = "EMAIL"
    FACT_NAME_ADDRESS = "ADDR"
    FACT_NAME_PHONE_HIGH_RECALL = "PHONE_high_recall"
    FACT_NAME_PHONE_HIGH_PRECISION = "PHONE_high_precision"
    FACT_NAME_PHONE_STRICT = "PHONE_strict"


    def __init__(
            self,
            original_text: str,
            dominant_language_code: str,
            analysis_lang: str,
            stanza_document: stanza.Document = None,
            entity_mapper: Optional[EntityMapper] = None,
            doc_path: str = "text_mlp",
            json_doc: dict = None,
            analyzers: list = [],
            error: str = "",
    ):

        self.original_text = original_text
        self.doc_path = doc_path
        self.analyzers = analyzers
        self.dominant_language_code = dominant_language_code
        self.analysis_lang = analysis_lang
        self.error = error
        self.json_doc = json_doc

        self.entities_processed = False

        self.entity_mapper = entity_mapper
        self.stanza_document = stanza_document

        self.__stanza_sentences = []
        self.__stanza_words = []
        self.__stanza_entities = []
        self.__words = []
        self.__lemmas = []
        self.__pos_tags = []
        self.__word_features = []
        self.__transliteration = []
        self.__texta_facts: List[Fact] = []

        self.__handle_existing_facts()

        if self.stanza_document:
            self.words()


    @property
    def stanza_sentences(self):
        if not self.__stanza_sentences and self.stanza_document:
            for sentence in self.stanza_document.sentences:
                self.__stanza_sentences.append(sentence)
        return self.__stanza_sentences


    @property
    def stanza_words(self):
        if not self.__stanza_words and self.stanza_document:
            for sentence in self.__stanza_sentences:
                for word in sentence.words:
                    self.__stanza_words.append(word)

        return self.__stanza_words


    @property
    def stanza_entities(self):
        if not self.__stanza_entities:
            for entity in self.stanza_document.entities:
                self.__stanza_entities.append(entity)
        return self.__stanza_entities


    def __get_doc_path(self, field: str) -> str:
        """
        :param field: Whether the doc_path uses the text or lemmas field.
        :return: MLP representation of the doc_path
        """
        content = f"{self.doc_path}_mlp.{field}"
        return content


    def __handle_existing_facts(self):
        """
        Add existing texta_facts inside the document into the private
        fact container variable so that they wouldn't be overwritten.
        """
        if self.json_doc:
            existing_facts = self.json_doc.get("texta_facts", [])
            facts = Fact.from_json(existing_facts)
            for fact in facts:
                self.add_fact(fact)

    @staticmethod
    def remove_duplicates_with_ignored_keys(duplicates, ignore_keys):
        seen = set()
        for duplicate in duplicates:
            index = frozenset((k, v) for k, v in duplicate.items() if k not in ignore_keys)
            if index not in seen:
                yield duplicate
                seen.add(index)

    @staticmethod
    def handle_null_values_in_facts(facts: List[dict]):
        container = []
        if facts:
            for fact in facts:
                new_fact = {key: value for key, value in fact.items() if value is not None}
                container.append(new_fact)
        return container


    @staticmethod
    def remove_duplicate_facts(facts: List[dict]):
        if facts:
            facts = Document.handle_null_values_in_facts(facts)
            without_duplicates = list(Document.remove_duplicates_with_ignored_keys(facts, ["id", "source"]))
            return without_duplicates
        else:
            return []

    def facts_to_json(self) -> dict:
        facts = [fact.to_json() for fact in self.__texta_facts]
        unique_facts = Document.remove_duplicate_facts(facts)
        return {"texta_facts": unique_facts}


    def add_fact(self, fact: Fact):
        self.__texta_facts.append(fact)


    def fact_spans_to_sent(self):
        """
        Updates fact spans to use sentence-based spans
        """
        tokenized_text = self.get_words()
        # browse throush facts
        for fact in self.__texta_facts:
            new_spans = []
            sent_index = 0
            for span in fact.spans:
                span_len = span[1]-span[0]
                sent_index = tokenized_text[:span[0]].count("\n")
                # find last sent break before the match
                matches = list(re.finditer(" \n ", tokenized_text[:span[0]]))
                # check if any sentences
                if matches:
                    # find the last sentence break
                    last_match = matches[-1]
                    # compute new spans in given sentence
                    new_start = span[0] - last_match.span()[1]
                    new_end = new_start + span_len
                    new_span = [new_start, new_end]
                    new_spans.append(new_span)
            # update spans in object
            if new_spans:
                fact.spans = new_spans
                fact.sent_index = sent_index


    @staticmethod
    def edit_doc(doc: dict, doc_path: str, new_value) -> dict:
        """
        :param doc: Original dictionary into which you add content.
        :param doc_path: Dot separated field paths to the nested value you wish to add.
        :param new_value: Value you wish to add into the nested path.
        :return: Dictionary with the new value added into it according to the path.
        """
        wrapper = PelicanJson(doc)
        path = doc_path.split(".")
        wrapper.set_nested_value(path, new_value, force=True)
        return wrapper.convert()


    @staticmethod
    def parse_doc(doc_path: str, document: dict) -> list:
        """
        Function for parsing text values from a nested dictionary given a field path.
        :param doc_path: Dot separated path of fields to the value we wish to parse.
        :param document: Document to be worked on.
        :return: List of text fields that will be processed by MLP.
        """
        wrapper = PelicanJson(document)
        doc_path_as_list = doc_path.split(".")
        content = wrapper.safe_get_nested_value(doc_path_as_list, default=[])
        if content and isinstance(content, str):
            return [content]
        # Check that content is non-empty list and there are only stings in the list.
        elif content and isinstance(content, list) and all([isinstance(list_content, str) for list_content in content]):
            return content
        # In case the field path is faulty and it gives you a dictionary instead.
        elif isinstance(content, dict):
            return []
        else:
            return []


    def document_to_json(self, use_default_doc_path=True) -> dict:
        """
        :param use_default_doc_path: Normal string values will be given the default path for facts but for dictionary input you already have them.
        """
        list_of_path_keys = self.doc_path.split(".")
        root_key = "{}_mlp".format(list_of_path_keys[-1])
        path_to_mlp = list_of_path_keys[:-1] + [root_key] if len(list_of_path_keys) > 1 else [root_key]
        mlp_result = self.to_json(use_default_doc_path)
        nested_dict_wrapper = PelicanJson(self.json_doc)
        nested_dict_wrapper.set_nested_value(path_to_mlp, mlp_result["text_mlp"], force=True)
        nested_dict_wrapper.set_nested_value(["texta_facts"], mlp_result["texta_facts"], force=True)

        return nested_dict_wrapper.convert()


    def to_json(self, use_default_doc_path=True) -> dict:
        container = dict()
        container["text"] = self.get_words()
        texta_facts = self.facts_to_json()
        container["language"] = {
            "detected": self.dominant_language_code,
            "analysis": self.analysis_lang
        }
        if self.error:
            container["error"] = self.error

        if "lemmas" in self.analyzers:
            container["lemmas"] = self.get_lemma()
        if "pos_tags" in self.analyzers:
            container["pos_tags"] = self.get_pos_tags()
        if "word_features" in self.analyzers:
            container["word_features"] = self.get_word_features()
        if "transliteration" in self.analyzers and self.__transliteration:
            container["transliteration"] = self.get_transliteration()
        if use_default_doc_path:
            for fact in texta_facts["texta_facts"]:
                fact["doc_path"] = "text_mlp.text"
        return {"text_mlp": container, **texta_facts}


    @staticmethod
    def _clean_lemma(lemma):
        if len(lemma) > 2:
            return lemma.replace("_", "").replace("=", "")
        return lemma


    def lemmas(self):
        for sent in self.stanza_sentences:
            self.__lemmas.append([self._clean_lemma(word.lemma) if word and word.lemma else "X" for word in sent.words])


    def get_lemma(self) -> str:
        sentences = []
        if not self.__lemmas:
            self.lemmas()
        for sent_lemmas in self.__lemmas:
            sentences.append(" ".join([a.strip() for a in sent_lemmas]))
        if "sentences" in self.analyzers:
            return " \n ".join(sentences)
        else:
            return " ".join(sentences)


    def sentences(self):
        pass


    def words(self):
        for sentence in self.stanza_sentences:
            self.__words.append([word.text for word in sentence.words])


    def get_words(self) -> str:
        if "sentences" in self.analyzers:
            return " \n ".join([" ".join(sent_words) for sent_words in self.__words])
        else:
            return " ".join([" ".join(sent_words) for sent_words in self.__words])


    def pos_tags(self):
        if "sentences" in self.analyzers:
            for i,sent in enumerate(self.stanza_sentences):
                tags_in_sent = [word.upos if word and word.upos and word.upos != "_" else "X" if word.upos == "_" else "X" for word in sent.words]
                for tag in tags_in_sent:
                    self.__pos_tags.append(tag)
                # if not last item
                if i+1 < len(self.stanza_sentences):
                    self.__pos_tags.append("LBR")
        else:
            self.__pos_tags = [word.upos if word and word.upos and word.upos != "_" else "X" if word.upos == "_" else "X" for word in self.stanza_words]


    def get_pos_tags(self) -> str:
        return " ".join([a.strip() for a in self.__pos_tags])


    def word_features(self):
        if "sentences" in self.analyzers:
            for i,sent in enumerate(self.stanza_sentences):
                tags_in_sent = [word.feats if word and word.feats and word.feats != "_" else "X" if word.feats == "_" else "X" for word in sent.words]
                for tag in tags_in_sent:
                    self.__word_features.append(tag)
                # if not last item
                if i+1 < len(self.stanza_sentences):
                    self.__word_features.append("LBR")
        else:
            self.__word_features = [word.feats if word and word.feats and word.feats != "_" else "X" if word.feats == "_" else "X" for word in self.stanza_words]


    def get_word_features(self) -> str:
        return " ".join([a.strip() for a in self.__word_features])


    def entities(self):
        """
        Retrieves list-based entities.
        """
        text = self.get_words()
        lemmas = self.get_lemma()

        hits = self.entity_mapper.map_entities(text)
        lemma_hits = self.entity_mapper.map_entities(lemmas, entity_types=["CURRENCY"])

        # make facts
        for entity_type, entity_values in hits.items():
            for entity_value in entity_values:
                new_fact = Fact(
                    source="mlp",
                    fact_type=entity_type,
                    fact_value=entity_value["value"],
                    doc_path=self.__get_doc_path("text"),
                    spans=[[entity_value["span"][0], entity_value["span"][1]]]
                )
                self.__texta_facts.append(new_fact)

        for entity_type, entity_values in lemma_hits.items():
            for entity_value in entity_values:
                new_fact = Fact(
                    source="mlp",
                    fact_type=entity_type,
                    fact_value=entity_value["value"],
                    doc_path=self.__get_doc_path("lemmas"),
                    spans=[[entity_value["span"][0], entity_value["span"][1]]]
                )
                self.__texta_facts.append(new_fact)

        # declare the entities processed
        self.entities_processed = True


    def currency_sum(self):
        """
        Extracts currency + sum and sum + currency patterns from text using regexp.
        Saves extractions as facts.
        """
        if not self.entities_processed:
            self.entities()

        text = self.get_words()
        currency_facts = [fact for fact in self.__texta_facts if fact.fact_type == "CURRENCY"]
        for fact in currency_facts:
            regexes = (
                f"{fact.fact_value} [0-9,\.]+",
                f"[0-9,\.]+ {fact.fact_value}[a-z]*"
            )
            for currency_regex in regexes:
                pattern = re.compile(currency_regex)
                for match in pattern.finditer(text):
                    fact_value = match.string[match.start():match.end()]
                    # recheck that string contains a number
                    if any(map(str.isdigit, fact_value)):
                        new_fact = Fact(
                            source="mlp",
                            fact_type="CURRENCY_SUM",
                            fact_value=fact_value,
                            doc_path=self.__get_doc_path("text"),
                            spans=[[match.start(), match.end()]]
                        )
                        self.__texta_facts.append(new_fact)


    def emails(self):
        text = self.get_words()
        emails = ContactEmailParser(text).parse()
        self.__texta_facts.extend((email.to_fact(Document.FACT_NAME_EMAIL, self.__get_doc_path("text")) for email in emails))


    def phone_strict(self):
        text = self.get_words()
        phone_numbers_strict = ContactPhoneParserStrict(text).parse()
        self.__texta_facts.extend(
            (number.to_fact(Document.FACT_NAME_PHONE_STRICT, self.__get_doc_path("text")) for number in phone_numbers_strict))


    def phone_high_recall(self):
        text = self.get_words()
        phone_numbers = ContactPhoneParserHighRecall(text, months=self.concat_resources["months"]).parse()
        self.__texta_facts.extend(
            (number.to_fact(Document.FACT_NAME_PHONE_HIGH_RECALL, self.__get_doc_path("text")) for number in phone_numbers))


    def phone_high_precision(self):
        text = self.get_words()
        phone_numbers_high_precision = ContactPhoneParserHighPrecision(text).parse()
        self.__texta_facts.extend((number.to_fact(Document.FACT_NAME_PHONE_HIGH_PRECISION, self.__get_doc_path("text")) for number in
                                   phone_numbers_high_precision))


    def addresses(self):
        text = self.get_words()
        addresses = AddressParser(text, self.stanza_entities, self.dominant_language_code).parse()
        self.__texta_facts.extend((addr.to_fact(Document.FACT_NAME_ADDRESS, self.__get_doc_path("text")) for addr in addresses))


    def transliteration(self):
        if self.dominant_language_code in Document.langs_to_transliterate:
            for word in self.stanza_words:
                if self.dominant_language_code == "ru":
                    translit_word = self._transliterate_russian_word(word.text)
                elif self.dominant_language_code == "ar":
                    translit_word = self._transliterate_arabic_word(word.text)
                self.__transliteration.append(translit_word)


    @staticmethod
    def _transliterate_russian_word(word: str):
        translit_word = russian_transliterator([word.strip()])
        try:
            translit_word = translit_word[0].strip()
        except IndexError:
            translit_word = word.strip()
        return translit_word


    @staticmethod
    def _transliterate_arabic_word(word):
        translit_word = buckwalter.transliterate(word.text.strip())
        if not translit_word:
            translit_word = word.text.strip()
        return translit_word


    def get_transliteration(self) -> str:
        return " ".join(['X' if not a.strip() else a for a in self.__transliteration])


    def entity_lemmas(self, entity_value):
        lemmas = ""
        splitted = entity_value.split(" ")
        for i, word in enumerate(self.stanza_words):
            if word.text == splitted[0]:
                if len(splitted) > 1:
                    isthatphrase = True
                    j = i
                    for entity_word in splitted[1:]:
                        j += 1
                        if j < len(self.stanza_words) and entity_word != self.stanza_words[j].text:
                            isthatphrase = False
                        if j >= len(self.stanza_words):
                            isthatphrase = False
                    if isthatphrase:
                        lemmas += word.lemma
                        for i_, entity_word in enumerate(splitted[1:]):
                            lemmas += " " + self.stanza_words[i_ + i + 1].text
                        return lemmas
                else:
                    return word.lemma
        return lemmas


    def ner(self):
        tokenized_text = self.get_words()
        for entity in self.stanza_entities:
            # finds the closest spans in tokenized text
            # this is because stanza returns spans from non-tokenized text
            pattern = re.compile(re.escape(entity.text))  # Use re.escape to avoid trouble with special characters existing in the text.
            matching_tokenized_spans = [(match.start(), match.end()) for match in pattern.finditer(tokenized_text)]
            best_matching_span = None
            best_matching_distance = math.inf
            non_tokenized_span = (entity.start_char, entity.end_char)
            # matching spans are always equal or larger
            for span in matching_tokenized_spans:
                span_distance = (span[0] - non_tokenized_span[0]) + (span[1] - non_tokenized_span[1])
                if abs(span_distance) < best_matching_distance:
                    best_matching_distance = abs(span_distance)
                    best_matching_span = span
            # create and append fact
            # ignore facts whose match fails
            if best_matching_span:
                text_before_match = tokenized_text[:best_matching_span[0]]
                sentence_index = text_before_match.count("\n")
                new_fact = Fact(
                    source="mlp",
                    fact_type=entity.type,
                    fact_value=entity.text,
                    doc_path=self.__get_doc_path("text"),
                    spans=[best_matching_span],
                    sent_index=sentence_index
                )
                self.__texta_facts.append(new_fact)
