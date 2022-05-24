import pandas as pd
import joblib

from sklearn.pipeline import Pipeline

from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
from tensorflow.keras.models import load_model

from TweetAnalysis.config.core import config
from TweetAnalysis.processing import preprocessing as pp
from TweetAnalysis import model as m


def read_data() -> pd.DataFrame:
    """making dataframe with the data"""

    # Importing the dataset
    df = pd.read_csv(config.app.DATA_FILE_PATH,
                     encoding=config.app.DATASET_ENCODING, names=config.app.DATASET_COLUMNS)

    df = df[[config.model.TARGET, 'text']]
    df[config.model.TARGET] = df[config.model.TARGET].replace(4, 1)

    df = df.sample(frac=1, random_state=config.app.SEED)

    return df


def get_value_target(df: pd.DataFrame):
    """get features and target"""

    X = df['text']
    y = df[config.model.TARGET]

    return X, y


def save_pipeline_keras(pipe, tokenizer_name=config.app.TOKENIZER_NAME, model_name=config.app.MODEL_NAME, classes_name=config.app.CLASSES_NAME) -> None:
    """Persist keras model to disk."""

    print("saving tokenizer...")
    joblib.dump(pipe.named_steps['tokenize'],
                config.app.MODELS_PATH + tokenizer_name)

    print("saving RNN model...")
    joblib.dump(pipe.named_steps['model'].classes_,
                config.app.MODELS_PATH + classes_name)
    pipe.named_steps['model'].model.save(
        config.app.MODELS_PATH + model_name)


def load_pipeline_keras() -> Pipeline:
    """Load a Keras Pipeline from disk."""

    print('loading tokenizer...')
    TokenizeText = joblib.load(config.app.MODELS_PATH + config.app.TOKENIZER_NAME)

    # print('loading word embeddings...')
    # embedding_matrix = joblib.load(config.EMBEDDING_MATRIX_PATH)

    print('loading RNN model...')
    def build_model(): return load_model(config.app.MODELS_PATH + config.app.MODEL_NAME)
    classifier = KerasClassifier(build_fn=build_model,
                                 batch_size=config.model.BATCH_SIZE,
                                 validation_split=0.1,
                                 epochs=config.model.EPOCHS,
                                 verbose=2,
                                 callbacks=m.callbacks,
                                 #  embedding_matrix=embedding_matrix
                                 )
    classifier.classes_ = joblib.load(config.app.MODELS_PATH + config.app.CLASSES_NAME)
    classifier.model = build_model()

    return Pipeline([
        ('tokenize', TokenizeText),
        ('pad', pp.PaddingText()),
        ('model', classifier)
    ])
