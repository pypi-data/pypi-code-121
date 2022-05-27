from scipy.special import softmax
import pandas as pd

from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig

from TweetAnalysis.config import logging_config 

_logger = logging_config.get_logger(__name__)


class SentimentPredictor:
    def __init__(self, model_path='F:\Big Projects\Twitter Analysis\\twitter-xlm-roberta-base-sentiment'):
        """ 
        Initialize the predictor.
        Args:
            model_path (str, optional): path to local model . Defaults to 'F:\Big Projects\Twitter Analysis\twitter-xlm-roberta-base-sentiment'.
        """
        _logger.info(f"Loading model {model_path}")

        MODEL = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL)
        self.config = AutoConfig.from_pretrained(MODEL)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL)
        # self.model.eval()

    def _preprocess(self, text):
        new_text = []
        for t in text.split(" "):
            t = '@user' if t.startswith('@') and len(t) > 1 else t
            t = 'http' if t.startswith('http') else t
            t = '' if t == 'RT' else t
            new_text.append(t)
        return " ".join(new_text)
    
    def predict(self, X: pd.Series):

        _logger.info(f"Predicting sentiment for {len(X)} tweets")

        df = pd.DataFrame({'tweet': X})
        df['text'] = df['tweet'].apply(lambda x: self._preprocess(x))
        encoded_inputs = self.tokenizer.batch_encode_plus(df['text'].tolist(), padding=True, return_tensors='pt')
        output = self.model(**encoded_inputs)
        scores = output[0].detach().numpy()
        scores = softmax(scores, axis=1)
        df_preds = pd.DataFrame(scores, columns=list(self.config.id2label.values()))
        df_preds['label'] = df_preds.idxmax(axis=1)
        df = pd.concat([df, df_preds], axis=1)

        _logger.info(f"Prediction complete")
        return df


