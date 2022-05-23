#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
import logging
import os
import random
import tempfile
from kolibri.data.text.resources import resources
from pathlib import Path
from kolibri.indexers import TextIndexer
from kolibri.task.text.topics.baseTopic import TopicModel
import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)

TOPIC_MODEL_FILE_NAME = "topic_model.pkl"


class TopicModelEstimator(TopicModel):
    """Python wrapper for LDA using `MALLET <http://mallet.cs.umass.edu/>`_.

    Communication between MALLET and Python takes place by passing around data files on disk
    and calling Java with subprocess.call().

    Warnings
    --------
    This is **only** python wrapper for `MALLET LDA <http://mallet.cs.umass.edu/>`_,
    you need to install original implementation first and pass the path to binary to ``mallet_path``.

    """


    provides = ["topics"]

    requires = ["tokens"]

    defaults = {
        "fixed": {
            "nb_topic_start": 1,
            "nb_topic_stop": 1,
            "step": 1,
            "workers": 4,
            "embeddings_dim": 50,
            "random_seed": 0,
            "output_folder": ".",
            "model": "lda",
            "algorithm": "gibbs"
        },
        "tunable": {
            "num_topics":{
                "value": 20,
                "type": "integer",
                "values":[20-30]
            } ,

            # The maximum number of iterations for optimization algorithms.
            "alpha": {
                "value": 50,
                "type": "integer",
                "values":[45-55]
            },
            "optimize_interval":{
                "value": 50,
                "type": "integer",
                "values":[45-55]
            },
            "iterations":{
                "value": 50,
                "type": "integer",
                "values":[45-55]
            },
            "topic_threshold":{
                "value": 200,
                "type": "integer",
                "values":[45-55]
            },
            "use_lemma":{
                "value": 50,
                "type": "categorical",
                "values":[True, False]
            },
        }
    }

    def __init__(self, component_config=None, prefix=None):

        super().__init__(component_config=component_config)
        self.start = self.get_parameter("nb_topic_start")
        self.stop = self.get_parameter("nb_topic_stop")
        self.step=self.get_parameter("step")

        self.indexer=TextIndexer()
        if self.start > self.stop:
            raise Exception("In topic experimentation start should be larger than stop.")
        self.model=None
        if self.get_parameter("algorithm")=="gibbs":
            self.mallet_path = resources.get(str(Path('modules', 'clustering', 'mallet'))).path
            self.mallet_path = os.path.join(self.mallet_path, 'bin/mallet')
        self.model_type=self.get_parameter("model", "lda")
        self.algorithm=self.get_parameter("algorithm", "gibbs")

        self.num_topics = self.get_parameter("num_topics")
        self.topic_threshold = self.get_parameter("topic_threshold")
        self.alpha = self.get_parameter("alpha")
        if prefix is None:
            rand_prefix = hex(random.randint(0, 0xffffff))[2:] + '_'
            prefix = os.path.join(tempfile.gettempdir(), rand_prefix)
        self.prefix = prefix
        self.workers = self.get_parameter("workers")
        self.optimize_interval = self.get_parameter("optimize_interval")
        self.iterations = self.get_parameter("iterations")
        self.random_seed = self.get_parameter("random_seed")
        self.topic_model = None

    def fit(self, X, y, X_val=None, y_val=None, **kwargs):
        """Train Mallet LDA.
        Parameters
        ----------
        corpus : iterable of iterable of (int, int)
            Corpus in BoW format
        """


        self.indexer.build_vocab(X, None)

        self.num_terms =len(self.indexer.token2idx)
        self.corpus = [self.indexer.doc2bow(doc) for doc in X]
        """

        This function trains a given topic model_type.
        Returns:
            Trained Model

        """

        multi_core=(self.get_parameter("n_jobs")==-1 or self.get_parameter("n_jobs")>1)
        import sys

        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        if logger.hasHandlers():
            logger.handlers.clear()

        ch = logging.FileHandler("logs.log")
        ch.setLevel(logging.DEBUG)



        logger.info(
            """fit(model_type=lda, multi_core={}, num_topics={})""".format(
                 str(self.get_parameter("n_jobs")==-1), str(self.num_topics)
            )
        )

        logger.info("Checking exceptions")

        # run_time
        import time

        runtime_start = time.time()

        # ignore warnings
        import warnings

        warnings.filterwarnings("ignore")

        # checking for allowed algorithms
        allowed_models = ["lda", "lsi", "hdp", "rp", "nmf"]

        if self.model_type not in allowed_models:
            sys.exit(
                "(Value Error): Model Not Available. Please see docstring for list of available models."
            )

        if self.num_topics is not None:
            if self.num_topics <= 1:
                sys.exit("(Type Error): num_topics parameter only accepts integer value.")



        model_fit_start = time.time()

        if self.model_type == "nmf":

            from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
            from sklearn.decomposition import NMF
            from sklearn.preprocessing import normalize

            logger.info(
                "CountVectorizer, TfidfTransformer, NMF, normalize imported successfully"
            )

            text_join = []

            for i in X:
                word = " ".join(i)
                text_join.append(word)

            self.vectorizer = CountVectorizer(analyzer="word", max_features=5000)
            x_counts = self.vectorizer.fit_transform(text_join)
            logger.info("CountVectorizer() Fit Successfully")
            self.transformer = TfidfTransformer(smooth_idf=False)
            x_tfidf = self.transformer.fit_transform(x_counts)
            logger.info("TfidfTransformer() Fit Successfully")
            xtfidf_norm = normalize(x_tfidf, norm="l1", axis=1)
            self.model = NMF(n_components=self.num_topics, init="nndsvd", random_state=self.get_parameter("seed"), **kwargs)
            self.model.fit(xtfidf_norm)
            logger.info("NMF() Trained Successfully")

        elif self.model_type == "lda":

            if multi_core:
                logger.info("LDA multi_core enabled")
                if self.algorithm=="variational":
                    from gensim.models.ldamulticore import LdaMulticore

                    logger.info("LdaMulticore imported successfully")

                    self.model = LdaMulticore(
                        corpus=self.corpus,
                        num_topics=self.num_topics,
                        id2word=self.indexer.idx2token,
                        workers=4,
                        random_state=self.get_parameter("seed"),
                        chunksize=100,
                        passes=10,
                        alpha="symmetric",
                        per_word_topics=True,
                        **kwargs
                    )

                    logger.info("LdaMulticore Variational model_type trained successfully")

                elif self.algorithm=="gibbs":
                    from kolibri.task.text.topics.mallet import LdaMallet
                    self.model=LdaMallet(self.mallet_path,
                                         corpus=self.corpus,
                                         iterations=self.iterations,
                                         num_topics=self.num_topics,
                                         id2word=self.indexer.idx2token,
                                         workers=4)

                    logger.info("LdaMulticore Gibbs model_type trained successfully")
            else:

                from gensim.models.ldamodel import LdaModel

                logger.info("LdaModel imported successfully")

                if self.get_parameter("algorithm")=="variational":

                    self.model = LdaModel(
                        corpus=self.corpus,
                        num_topics=self.num_topics,
                        id2word=self.indexer.idx2token,
                        random_state=self.get_parameter("seed"),
                        update_every=1,
                        chunksize=100,
                        passes=10,
                        alpha="auto",
                        per_word_topics=True,
                        **kwargs
                    )

                    logger.info("LdaModel trained successfully")


                elif self.get_parameter("algorithm") == "gibbs":
                    from kolibri.task.text.topics.mallet import LdaMallet
                    self.model = LdaMallet(self.mallet_path,
                                           corpus=self.corpus,
                                           iterations=self.iterations,
                                           num_topics=self.num_topics,
                                           id2word=self.indexer.idx2token)

                    logger.info("LdaMulticore Gibbs model_type trained successfully")


        elif self.model_type == "lsi":

            from gensim.models.lsimodel import LsiModel

            logger.info("LsiModel imported successfully")

            self.model = LsiModel(corpus=self.corpus, num_topics=self.num_topics, id2word=self.indexer.idx2token, **kwargs)

            logger.info("LsiModel trained successfully")


        elif self.model_type == "hdp":

            from gensim.models import HdpModel

            logger.info("HdpModel imported successfully")

            self.model = HdpModel(
                corpus=self.corpus,
                id2word=self.indexer.idx2token,
                random_state=self.get_parameter("seed"),
                chunksize=100,
                T=self.num_topics,
                **kwargs
            )

            logger.info("HdpModel trained successfully")


        elif self.model_type == "rp":

            from gensim.models import RpModel

            logger.info("RpModel imported successfully")

            self.model = RpModel(corpus=self.corpus, id2word=self.indexer.idx2token, num_topics=self.num_topics, **kwargs)

            logger.info("RpModel trained successfully")


        logger.info(str(self.model))
        logger.info(
            "fit() succesfully completed......................................"
        )

    def predict(self, X, verbose=True):

            """
            This function assigns topic labels to the dataset for a given model_type.



            model_type: trained model_type object, default = None
                Trained model_type object


            verbose: bool, default = True
                Status update is not printed when verbose is set to False.


            Returns:
                pandas.DataFrame

            """

            if self.model_type == "lda":
                corpus = [self.indexer.doc2bow(doc) for doc in X]
                if self.algorithm == "variational":
                    pred = self.model.get_document_topics(corpus, minimum_probability=0)
                elif self.algorithm == "gibbs":
                    pred = self.model.get_document_topics(corpus)
                return [{t:p for t,p in d} for d in pred]
            elif self.model_type == "lsi":
                pred=[]
                for i in range(0, len(X)):
                    db = self.indexer.doc2bow(X[i])
                    db_ = self.model[db]
                    pred.append(db_)

                return [{t:p for t,p in d} for d in pred]

            elif self.model_type == "hdp" or self.model_type == "rp":
                corpus = [self.indexer.doc2bow(doc) for doc in X]
                rate = []
                for i in range(0, len(X)):
                    rate.append(self.model[corpus[i]])

                return [{t:p for t,p in d} for d in rate]

            elif self.model_type == "nmf":

                """
                this section will go away in future release through better handling
                """

                from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
                from sklearn.decomposition import NMF
                from sklearn.preprocessing import normalize

                text_join = []

                for i in X:
                    word = " ".join(i)
                    text_join.append(word)

                x_counts = self.vectorizer.transform(text_join)
                x_tfidf = self.transformer.transform(x_counts)
                xtfidf_norm = normalize(x_tfidf, norm="l1", axis=1)

                """
                section ends
                """

                bb = list(self.model.transform(xtfidf_norm))



            return [{i:t for i, t in enumerate(d)} for d in bb]

    @classmethod
    def load(cls,
             model_dir=None,
             model_metadata=None,
             cached_component=None,
             **kwargs
             ):

        file_name = model_metadata.get("topic_file", TOPIC_MODEL_FILE_NAME)
        classifier_file = os.path.join(model_dir, file_name)
        import joblib
        if os.path.exists(classifier_file):
            model = joblib.load(classifier_file)

            return model
        else:
            return cls(model_metadata)

    def persist(self, model_dir):
        """Persist this model_type into the passed directory."""

        classifier_file = os.path.join(model_dir, TOPIC_MODEL_FILE_NAME)
        import joblib

        joblib.dump(self, classifier_file)

        return {"topic_file": TOPIC_MODEL_FILE_NAME}





def get_available_models():

    """
    Returns table of models available in model_type library.


    Example
    -------
    >>> from kolibri.task.text.topics import get_available_models
    >>> all_models = available_models()


    Returns:
        pandas.DataFrame

    """

    import pandas as pd

    model_id = ["lda", "lda", "lsi", "hdp", "rp", "nmf"]

    algorithms=["variational", "gibbs", None, None, None, None]
    model_name = [
        "Latent Dirichlet Allocation",
        "Latent Dirichlet Allocation",
        "Latent Semantic Indexing",
        "Hierarchical Dirichlet Process",
        "Random Projections",
        "Non-Negative Matrix Factorization",
    ]


    df = pd.DataFrame({"ID": model_id, "algorithm": algorithms, "Name": model_name})

    df.set_index("ID", inplace=True)

    return df


from kolibri.registry import ModulesRegistry
ModulesRegistry.add_module(TopicModelEstimator.name, TopicModelEstimator)
