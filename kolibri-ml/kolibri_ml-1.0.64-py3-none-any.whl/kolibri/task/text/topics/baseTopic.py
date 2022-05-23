from kolibri.logger import get_logger
from kolibri.backend.base.estimator import BaseEstimator


logger=get_logger(__name__)


class TopicModel(BaseEstimator):

    def __init__(self, component_config,  display_output=True):

        super().__init__(component_config)
        self.diplay_outoput=display_output
        try:
            import psutil

            logger.info("Memory: " + str(psutil.virtual_memory()))
            logger.info("Physical Core: " + str(psutil.cpu_count(logical=False)))
            logger.info("Logical Core: " + str(psutil.cpu_count(logical=True)))
        except:
            logger.warning(
                "cannot find psutil installation. memory not traceable. Install psutil using pip to enable memory logging. "
            )

        logger.info("Checking libraries")
        try:
            import warnings

            warnings.filterwarnings("ignore")
            from gensim import __version__

            logger.info("gensim==" + str(__version__))
        except:
            logger.warning("gensim not found")

        try:
            from pyLDAvis import __version__

            logger.info("pyLDAvis==" + str(__version__))
        except:
            logger.warning("pyLDAvis not found")

        try:
            from wordcloud import __version__

            logger.info("wordcloud==" + str(__version__))
        except:
            logger.warning("wordcloud not found")

            import datetime, time

            runtime_start = time.time()

            # ignore warnings
            import warnings

            warnings.filterwarnings("ignore")
        import pandas as pd
        import ipywidgets as ipw
        from IPython.display import display, HTML, clear_output, update_display
        import datetime, time

        logger.info("Preparing display monitor")

        # progress bar
        max_steps = 11
        total_steps = 9

        progress = ipw.IntProgress(
            value=0, min=0, max=max_steps, step=1, description="Processing: "
        )


    def print_topic(self, topicno, topn=10):
        """Get a single topic as a formatted string.

        Parameters
        ----------
        topicno : int
            Topic id.
        topn : int
            Number of words from topic that will be used.

        Returns
        -------
        str
            String representation of topic, like '-0.340 * "category" + 0.298 * "$M$" + 0.183 * "algebra" + ... '.

        """
        return ' + '.join('%.3f*"%s"' % (v, k) for k, v in self.show_topic(topicno, topn))

    def print_topics(self, num_topics=20, num_words=10):
        """Get the most significant topics (alias for `show_topics()` method).

        Parameters
        ----------
        num_topics : int, optional
            The number of topics to be selected, if -1 - all topics will be in result (ordered by significance).
        num_words : int, optional
            The number of words to be included per topics (ordered by significance).

        Returns
        -------
        list of (int, list of (str, float))
            Sequence with (topic_id, [(word, value), ... ]).

        """
        return self.show_topics(num_topics=num_topics, num_words=num_words, log=True)

    def get_topics(self):
        """Get words data topics matrix.

        Returns
        --------
        numpy.ndarray:
            The term topic matrix learned during inference, shape (`num_topics`, `vocabulary_size`).

        Raises
        ------
        NotImplementedError

        """
        raise NotImplementedError