from typing import Any, List, Dict, NamedTuple
from pydantic import BaseModel, PrivateAttr, validator
import ktrain
from cached_path import cached_path

from tensorflow.keras import mixed_precision  # erroneous missing import
import tensorflow as tf

if len(tf.config.list_physical_devices('GPU')) > 0:
    mixed_precision.set_global_policy('mixed_float16')


class Prediction(NamedTuple):
    document: Dict[str, str]
    classification: int
    probability: float


class Classifier(BaseModel):
    """
    Classifier to identify articles with biological pathway information.

    Attributes
    ----------
    model_url : str
        A url to a previously saved Predictor instance model
    threshold : float
        Minimum probability for classification to equal 1

    Methods
    ----------
    predict(self, documents: List[Dict[str, str]]) -> List[Prediction]
        Return a Prediction based upon the text information in incoming docuemnts
    """

    model_url: str = (
        "https://github.com/PathwayCommons/pathway-abstract-classifier/"
        "releases/download/pretrained-models/title_abstract_model.zip"
    )
    threshold: float = 0.5
    _model: Any = PrivateAttr()
    _sep_token: str = PrivateAttr()

    @validator("threshold")
    def min_threshold_is_nonneg_lt_one(cls, v):
        if v < 0 or v > 1:
            raise ValueError("Must be float on [0, 1]")
        return v

    def __init__(self, **data: Any) -> None:
        """Initializes Classifier instance"""
        super().__init__(**data)
        model_path = cached_path(self.model_url, extract_archive=True)
        self._model = ktrain.load_predictor(model_path)
        self._sep_token = self._model.preproc.get_tokenizer().sep_token

    def _to_texts(
        self, documents: List[Dict[str, str]], fields: List[str] = ["title", "abstract"]
    ) -> List[str]:
        """Map the text fields to a single string"""
        texts = []
        for document in documents:
            tokens: List[str] = []
            for field in fields:
                if field in document:
                    value = document[field]
                    if value is not None and len(value) > 0:
                        if len(tokens) > 0:
                            tokens.append(self._sep_token)
                        tokens.append(value)
            texts.append(" ".join(tokens))
        return texts

    def _to_predictions(
        self, documents: List[Dict[str, str]], probabilities: List[float]
    ) -> List[Prediction]:
        """Format the incoming data with the prediction results"""
        results = []
        for index, document in enumerate(documents):
            results.append(
                Prediction(
                    document,
                    int(probabilities[index] >= self.threshold),
                    float(probabilities[index]),
                )
            )
        return results

    def predict(self, documents: List[Dict[str, str]]) -> List[Prediction]:
        """Predictions based on text in documents"""
        texts = self._to_texts(documents)
        probabilities = self._model.predict_proba(texts)[:, 1]
        return self._to_predictions(documents, probabilities)
