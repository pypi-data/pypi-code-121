import logging
import os
import pathlib
import shutil
from typing import List, Optional
from urllib.parse import urlparse
from urllib.request import urlopen

import regex as re
import stanza
import torch
from bs4 import BeautifulSoup
from langdetect import detect

from texta_mlp.document import Document
from texta_mlp.entity_mapper import EntityMapper
from texta_mlp.exceptions import CUDAException, LanguageNotSupported
from texta_mlp.settings import (CUSTOM_NER_MODELS, CUSTOM_NER_MODEL_LANGS, DEFAULT_ANALYZERS, DEFAULT_DOC_PATH_KEY, DEFAULT_LANG_CODES, DEFAULT_OUTPUT_KEY, DEFAULT_RESOURCE_DIR, ENTITY_MAPPER_DATA_URLS, META_KEY, REFRESH_DATA, STANZA_NER_SUPPORT, SUPPORTED_ANALYZERS, USE_GPU)


class MLP:

    def __init__(
            self,
            language_codes=DEFAULT_LANG_CODES,
            default_language_code=DEFAULT_LANG_CODES[0],
            use_default_language_code=True,
            resource_dir: str = DEFAULT_RESOURCE_DIR,
            ner_model_langs: list = CUSTOM_NER_MODEL_LANGS,
            logging_level: str = "error",
            use_gpu: bool = USE_GPU,
            gpu_device_id: int = 0,
            refresh_data: bool = REFRESH_DATA
    ):
        self.supported_langs = language_codes
        self.logger = logging.getLogger()
        self.default_lang = default_language_code
        self.use_default_lang = use_default_language_code
        self.resource_dir = resource_dir

        self._stanza_pipelines = {}
        self.custom_ner_model_langs = ner_model_langs
        self.logging_level = logging_level
        self.stanza_resource_path = pathlib.Path(self.resource_dir) / "stanza"
        self.custom_ner_model_Path = pathlib.Path(self.resource_dir) / "ner_models"
        self.prepare_resources(refresh_data)
        self._entity_mapper = None
        self.loaded_entity_files = []

        self.use_gpu = use_gpu
        if self.use_gpu:
            # check if cuda available
            if not torch.cuda.is_available():
                raise CUDAException("Your machine does not support CUDA!")
            # select gpu based on env
            if gpu_device_id > 0:
                device_count = torch.cuda.device_count()
                if gpu_device_id > device_count - 1:
                    raise CUDAException(f"Invalid device id: {gpu_device_id}! Your machine only has {device_count} device(s).")
                torch.cuda.set_device(gpu_device_id)


    def prepare_resources(self, refresh_data):
        """
        Prepares all resources for MLP.
        """
        # delete data if refresh asked
        if refresh_data:
            shutil.rmtree(self.resource_dir)
            self.logger.info("MLP data directory deleted.")
        # download resources
        self.download_custom_ner_models(self.resource_dir, logger=self.logger, model_langs=self.custom_ner_model_langs)
        self.download_stanza_resources(self.resource_dir, self.supported_langs, logger=self.logger)
        self.download_entity_mapper_resources(self.resource_dir, logger=self.logger)


    @staticmethod
    def download_custom_ner_models(resource_dir: str, logger=None, custom_ner_model_urls: dict = CUSTOM_NER_MODELS, model_langs: list = None):
        """
        Downloads custom ner models if not present in resources directory.
        """
        ner_resource_dir = pathlib.Path(resource_dir) / "ner_models"
        ner_resource_dir.mkdir(parents=True, exist_ok=True)
        for lang, url in custom_ner_model_urls.items():
            if lang in model_langs:
                file_name = urlparse(url).path.split("/")[-1]
                file_path = ner_resource_dir / lang
                if not file_path.exists():
                    if logger: logger.info(f"Downloading custom ner model file {file_name} into directory: {url}")
                    response = urlopen(url)
                    content = response.read()
                    with open(file_path, "wb") as fh:
                        fh.write(content)


    @staticmethod
    def download_stanza_resources(resource_dir: str, supported_langs: List[str], logger=None):
        """
        Downloads Stanza resources if not present in resources directory.
        By default all is downloaded into data directory under package directory.
        """
        model_types = ["depparse", "lemma", "pos", "tokenize"]
        stanza_resource_path = pathlib.Path(resource_dir) / "stanza"
        if logger:
            logger.info(f"Downloading Stanza models into the directory: {str(stanza_resource_path)}")

        stanza_resource_path.mkdir(parents=True, exist_ok=True)  # Create the directories with default permissions including parents.
        for language_code in supported_langs:
            # rglob is for recursive filename pattern matching, if it matches nothing
            # then the necessary files do not exist and we should download them.
            lang_dir_exists = True if list(stanza_resource_path.rglob("{}*".format(language_code))) else False
            model_folders_exists = all([(stanza_resource_path / language_code / model_type).exists() for model_type in model_types])
            if not (lang_dir_exists and model_folders_exists):
                stanza.download(language_code, str(stanza_resource_path))


    @staticmethod
    def download_entity_mapper_resources(resource_dir: str, logger=None, entity_mapper_urls: tuple = ENTITY_MAPPER_DATA_URLS):
        entity_mapper_resource_path = pathlib.Path(resource_dir) / "entity_mapper"
        entity_mapper_resource_path.mkdir(parents=True, exist_ok=True)
        for url in entity_mapper_urls:
            file_name = urlparse(url).path.split("/")[-1]
            file_path = entity_mapper_resource_path / file_name
            if not file_path.exists():
                if logger: logger.info(f"Downloading entity mapper file {file_name} into the directory: {url}")
                response = urlopen(url)
                content = response.read().decode()
                with open(file_path, "w", encoding="utf8") as fh:
                    fh.write(content)


    def _load_entity_mapper(self):
        # create Entity Mapper instance
        data_dir = os.path.join(self.resource_dir, "entity_mapper")
        data_files = [os.path.join(data_dir, path) for path in os.listdir(data_dir)]
        self.loaded_entity_files = data_files
        return EntityMapper(data_files)


    @staticmethod
    def normalize_input_text(text: str) -> str:
        """
        Normalizes input text so it won't break anything.
        :param: str text: Input text.
        :return: Normalized text.
        """
        text = str(text)
        bs = BeautifulSoup(text, "lxml")
        text = bs.get_text(' ')  # Remove html.
        text = re.sub('(\n){2,}', '\n\n', text)
        text = re.sub('( )+', ' ', text)
        text = text.strip()
        return text


    def detect_language(self, text: str) -> Optional[str]:
        """
        Detects language of input text.
        If language not in supported list, language is defaulted or exception raised.
        :param: str text: Text to be analyzed.
        :return: Language code.
        """
        # try to detect language
        try:
            lang = detect(text)
        except:
            lang = None
        return lang


    def generate_document(self, raw_text: str, analyzers: List[str], json_object: dict = None, doc_paths=DEFAULT_DOC_PATH_KEY, lang=None, stanza_document=None):
        processed_text = MLP.normalize_input_text(raw_text)
        e = ""

        # detect language
        if not lang:
            lang = self.detect_language(processed_text)
        '''
        check if detected language is supported if the language is not supported it will use default_lang to load
        stanza models yet keep the document lang as the detected language
        '''
        # Resolve the language.
        if lang not in self.supported_langs:
            analysis_lang = self.default_lang
        else:
            analysis_lang = lang

        # Use the pre-given document if it exists, otherwise calculate on own.
        if processed_text and stanza_document is None:
            document, e = self._get_stanza_document(analysis_lang, processed_text) if processed_text else (None, "")
        elif stanza_document and processed_text:
            document = stanza_document
        else:
            document = None

        # Create the overall wrapper.
        document = Document(
            original_text=processed_text,
            dominant_language_code=lang,
            analysis_lang=analysis_lang,
            stanza_document=document,
            analyzers=analyzers,
            json_doc=json_object,
            doc_path=doc_paths,
            entity_mapper=self.get_entity_mapper(),
            error=e
        )
        return document


    @staticmethod
    def _load_analyzers(analyzers, supported_analyzers):
        if analyzers == ["all"]:
            return [analyzer for analyzer in supported_analyzers if analyzer != "all"]
        return [analyzer for analyzer in analyzers if (analyzer in supported_analyzers and analyzer != "all")]


    def get_entity_mapper(self):
        if self._entity_mapper is None:
            self._entity_mapper = self._load_entity_mapper()
        return self._entity_mapper


    def get_stanza_pipeline(self, lang: str):
        if lang not in self._stanza_pipelines:
            if lang in self.custom_ner_model_langs:
                self._stanza_pipelines[lang] = stanza.Pipeline(
                    lang=lang,
                    dir=str(self.stanza_resource_path),
                    processors=self._get_stanza_processors(lang),
                    ner_model_path=f"{self.custom_ner_model_Path}/{lang}",
                    use_gpu=self.use_gpu,
                    logging_level=self.logging_level,
                )
            else:
                self._stanza_pipelines[lang] = stanza.Pipeline(
                    lang=lang,
                    dir=str(self.stanza_resource_path),
                    processors=self._get_stanza_processors(lang),
                    use_gpu=self.use_gpu,
                    logging_level=self.logging_level,
                )
        return self._stanza_pipelines[lang]


    def _get_stanza_document(self, lang: str, raw_text: str):
        e = ""
        try:
            document = self.get_stanza_pipeline(lang)(raw_text)
            return document, e
        except KeyError as e:
            raise LanguageNotSupported(f"Language {lang} not supported. Check the list of supported languages.")

        except Exception as e:
            self.logger.exception(e)
            return None, repr(e)


    def _get_stanza_ner(self, lang: str, raw_text: str):
        pipeline = self.get_stanza_pipeline(lang)(raw_text)
        return [entity for sentence in pipeline.sentences for entity in sentence.entities]


    @staticmethod
    def _get_stanza_processors(lang):
        """
        Returns processor options based on language and NER support in Stanza.
        """
        if lang in STANZA_NER_SUPPORT:
            return "tokenize,pos,lemma,ner"
        else:
            return "tokenize,pos,lemma"


    def process(self, raw_text: str, analyzers: list = DEFAULT_ANALYZERS, lang=None, spans: str = "text"):
        """
        Processes raw text.
        :param: raw_text str: Text to be processed.
        :param: analyzers list: List of analyzers to be used.
        :return: Processed text as document ready for Elastic.
        """
        loaded_analyzers = self._load_analyzers(analyzers, SUPPORTED_ANALYZERS)
        document = self.generate_document(raw_text, loaded_analyzers, lang=lang)

        if document:
            for analyzer in loaded_analyzers:
                # For every analyzer, activate the function that processes it from the
                # document class.
                self.__apply_analyzer(document, analyzer)

            if "sentences" in loaded_analyzers and spans == "sentence":
                document.fact_spans_to_sent()

            result = document.to_json()
            result = self.__add_meta_to_mlp_output(result, DEFAULT_OUTPUT_KEY, loaded_analyzers, spans)
            return result
        else:
            return None


    def lemmatize(self, raw_text: str, lang=None):
        """
        Lemmatizes input text.
        :param: raw_text str: Text to be lemmatized.
        :return: Lemmatized string.
        """
        document = self.process(raw_text, analyzers=["lemmas"], lang=lang)
        return document["text_mlp"]["lemmas"]


    def __apply_analyzer(self, doc, analyzer):
        try:
            getattr(doc, analyzer)()
        except Exception as e:
            self.logger.exception(e)


    def __add_meta_to_mlp_output(self, result: dict, field: str, analyzers: List[str], spans: str):
        """Helper function to add meta information to an MLP document that has finished processing."""
        if META_KEY not in result:
            result[META_KEY] = {}

        tokenization = "sentence" if "sentences" in analyzers else "text"
        spans = "sentence" if "sentences" in analyzers and spans == "sentence" else "text"
        result[META_KEY][field] = {
            "tokenization": tokenization,
            "spans": spans,
            "analyzers": analyzers
        }
        return result


    def process_docs(self, docs: List[dict], doc_paths: List[str], analyzers=DEFAULT_ANALYZERS, spans: str = "text"):
        """
        :param docs: Contains tuples with two dicts inside them, the first being the document to be analyzed and the second is the meta information that corresponds to the document for transport purposes later on.
        :param doc_paths: Dot separated paths for how to traverse the dict for the text value you want to analyze.
        :param analyzers: List of strings to determine which procedures you want your text to be analyzed with.
        :return: List of dictionaries where the mlp information is stored inside texta_facts and the last field of the doc_path in the format {doc_path}_mlp.
        """
        # Container for keeping the tuples of the doc and meta pairs.
        analyzers = self._load_analyzers(analyzers, SUPPORTED_ANALYZERS)

        for doc_path in doc_paths:
            lang_group = {}
            texts = [Document.parse_doc(doc_path, document) for document in docs]
            for index, text in enumerate(texts):
                text = text[0] if text else ""
                lang = self.detect_language(text)
                if lang not in self.supported_langs:
                    lang = self.default_lang
                if lang and lang not in lang_group:
                    lang_group[lang] = [{"index": index, "text": text}]
                elif lang in lang_group:
                    lang_group[lang].append({"index": index, "text": text})

            intermediary = []
            for lang, items in lang_group.items():
                pipeline = self.get_stanza_pipeline(lang)
                # Create the batch of Stanza Documents to feed into the pipeline.
                documents = []
                for item in items:
                    text = item.get("text", "")
                    text = text if text else ""
                    documents.append(stanza.Document([], text=text))
                # Analyze the batch.
                results = pipeline(documents)
                for index, result in enumerate(results):
                    actual_index = items[index]["index"]
                    # Tie together the original document and it's location in the list for replacement and the relevant Stanza document.
                    intermediary.insert(actual_index, ({"actual_doc": docs[actual_index], "actual_index": actual_index, "lang": lang}, result))

            for meta_info, stanza_document in intermediary:
                # Traverse the (possible) nested dicts and extract their text values from it as a list of strings.
                # Since the nested doc_path could lead to a list there are multiple pieces of text which would be needed to process.

                actual_document = meta_info["actual_doc"]
                actual_index = meta_info["actual_index"]
                lang = meta_info["lang"]
                doc_texts = Document.parse_doc(doc_path, actual_document)
                for raw_text in doc_texts:
                    doc = self.generate_document(raw_text, analyzers=analyzers, json_object=actual_document, lang=lang, stanza_document=stanza_document, doc_paths=doc_path, )
                    if doc:
                        for analyzer in analyzers:
                            # For every analyzer, activate the function that processes it from the
                            # document class.
                            self.__apply_analyzer(doc, analyzer)

                        if "sentences" in analyzers and spans == "sentence":
                            doc.fact_spans_to_sent()

                        result = doc.document_to_json(use_default_doc_path=False)
                        result = self.__add_meta_to_mlp_output(result, doc_path, analyzers, spans)
                        docs[actual_index] = result

        return docs
