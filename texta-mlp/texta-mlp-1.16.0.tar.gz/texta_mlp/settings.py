import os
from texta_mlp.utils import parse_bool_env


META_KEY = "_mlp_meta"

DEFAULT_DOC_PATH_KEY = "text"
DEFAULT_OUTPUT_KEY = "text_mlp"

# Languages supported by default.
DEFAULT_LANG_CODES = ("et", "ru", "en", "ar")

# URLs for default Entity Mapper data sources.
ENTITY_MAPPER_DATA_URLS = (
    "https://packages.texta.ee/texta-resources/entity_mapper/addresses.json",
    "https://packages.texta.ee/texta-resources/entity_mapper/companies.json",
    "https://packages.texta.ee/texta-resources/entity_mapper/currencies.json"
)

# URLs for Custom NER model downloads.
CUSTOM_NER_MODELS = {
    "et": "https://packages.texta.ee/texta-resources/ner_models/_estonian_nertagger.pt",
}

# Location of the resource dir where models are downloaded
DEFAULT_RESOURCE_DIR = os.getenv("TEXTA_MLP_DATA_DIR", os.path.join(os.getcwd(), "data"))

# Data refresh means deleting all existing models and downloading new ones
REFRESH_DATA = parse_bool_env("TEXTA_MLP_REFRESH_DATA", False)

# List of all analyzers supported by MLP
SUPPORTED_ANALYZERS = (
    "lemmas",
    "pos_tags",
    "word_features",
    "transliteration",
    "ner",
    "addresses",
    "emails",
    "phone_strict",
    "entities",
    "currency_sum",
    "sentences"
)

DEFAULT_ANALYZERS = [
    "lemmas",
    "pos_tags",
    "word_features",
    "transliteration",
    "ner",
    "addresses",
    "emails",
    "phone_strict",
    "entities",
    "sentences",
    "currency_sum"
]


# Here we define languages with NER support to avoid Stanza trying to load them for languages without NER support.
# This significantly increases performance for languages without NER.
# https://stanfordnlp.github.io/stanza/available_models.html#available-ner-models
STANZA_NER_SUPPORT = ("ar", "zh", "nl", "en", "fr", "de", "ru", "es", "uk")

# Here we add langs that will have custom ner models.
CUSTOM_NER_MODEL_LANGS = ["et"]

# Use gpu for pytorch
USE_GPU = parse_bool_env("TEXTA_MLP_USE_GPU", False)
