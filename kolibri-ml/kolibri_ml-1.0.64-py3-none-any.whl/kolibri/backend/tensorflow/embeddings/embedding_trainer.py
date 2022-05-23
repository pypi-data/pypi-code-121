import os

from kolibri import Component
from kolibri.document import Document
from kolibri.settings import EMBEDDING_SIZE
from kolibri.tools.word2vec import train_word2vec, fit_scaler
from kolibri.utils.file import save_to_disk, load_from_disk

W2V_FILENAME = "word2vec.model"
SCALER_FILENAME = "scaler.model"


class EmbeddingTrainer(Component):
    name = "embedding_trainer"

    provides = ["embedding"]
    defaults = {
        "embedding_path": None,
        "embeddings_dim": EMBEDDING_SIZE
    }

    def __init__(self, config={}):
        super().__init__(config)
        self.embedding_size = self.component_config["embeddings_dim"]

    def train(self, training_data, **kwargs):

        self.train_word2vec(training_data, self.embedding_size)
        self.fit_scaler(training_data)
        self.save_scaler()
        self.save_word2vec_model()

    def transform(self, data, **kwargs):

        return

    def process(self, document: Document, **kwargs):
        return

    def train_word2vec(self, trainingdata, vec_dim=EMBEDDING_SIZE):
        """
        Train the word2vec model on a directory with text files.
        :param train_dir: directory with '.txt' files
        :param vec_dim: dimensionality of the word vectors

        :return: trained gensim model
        """

        self.word2vec_model = train_word2vec(trainingdata, vec_dim=vec_dim)

        return self.word2vec_model

    def fit_scaler(self, train_data):
        """
        Fit a scaler on given texts. Word vectors must be trained already.
        :param train_dir: directory with '.txt' files

        :return: fitted scaler object
        """
        if not self.word2vec_model:
            raise ValueError('word2vec model is not trained. ' + \
                             'Run train_word2vec() first.')

        self.scaler = fit_scaler(train_data, word2vec_model=self.word2vec_model)

        return self.scaler

    def save_scaler(self, overwrite=True):
        """ Save the scaler object to a file """
        if not self.scaler:
            raise ValueError("Can't save the scaler, " + \
                             "it has not been trained yet")
        save_to_disk(os.path.join(self.component_config['output-folder'], SCALER_FILENAME), self.scaler,
                     overwrite=overwrite)

    def load_scaler(self):
        """ Load the scaler object from a file """
        self.scaler = load_from_disk(os.path.join(self.component_config['output-folder'], SCALER_FILENAME))

    def save_word2vec_model(self, overwrite=True):
        """ Save the word2vec model to a file """
        if not self.word2vec_model:
            raise ValueError("Can't save the word2vec model, " + \
                             "it has not been trained yet")
        save_to_disk(os.path.join(self.component_config["output-folder"], W2V_FILENAME), self.word2vec_model,
                     overwrite=overwrite)

    def load_word2vec_model(self):
        """ Load the word2vec model from a file """
        self.word2vec_model = load_from_disk(os.path.join(self.component_config["embedding_path"], W2V_FILENAME))
        return self.word2vec_model

    def get_info(self):
        return "word_tokenizer"
