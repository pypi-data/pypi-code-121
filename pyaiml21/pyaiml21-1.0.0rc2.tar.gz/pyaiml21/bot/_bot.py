from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from pyaiml21.botconfig import BotConfig
from pyaiml21.parser import Logger
from pyaiml21.graphmaster import StarBindings
from pyaiml21.ast import Node


class Bot(ABC):
    """
    Abstract class from which the chatbot should inherit.

    This class provides an interface based on which the interpreter and
    implementation in stdlib/ evaluates the <template> tag.
    """

    def __init__(self):
        """Create the bot."""
        self.config = BotConfig()

    @abstractmethod
    def preprocess(self, text: str) -> List[str]:
        """
        Preprocess the input text `text`.

        Normalize the text, remove punctuation and strip it to sentences.

        :param text: the text to be normalized
        :return: sentences extracted from the text
        """

    @abstractmethod
    def search_brain(self, user_id: str, sentence: str)\
            -> Optional[Tuple[Node, StarBindings, bool]]:
        """
        Search the bot's brain and return the appropriate template node.

        :param user_id: user from the bot-client conversation
        :param sentence: normalized sentence for which to find the template
        :return: None if no match was found, else triple with template node,
            matched stars and flag signalizing whether the match was exact
            using $WORD
        """

    @abstractmethod
    def respond(self, input_: str, user_id: str) -> str:
        """
        Search graphmaster and return the reply to `input_`.

        :param user_id: user id for whom to search
        :param input_: user input to match
        :return: the bot's reply
        """

    @abstractmethod
    def get_predicate(self, name: str, user_id: str) -> str:
        """
        Find and return the value of a bot's _predicate.

        :param name: name of the _predicate
        :param user_id: current user we are chatting with
        :return: the _predicate value or `self.config.default_predicate`
        """

    def get_property(self, name: str) -> str:
        """
        Return the bot's property value.

        If it is not defined, return default bot's property or
        default _predicate value - the first one that is defined.

        :param name: name of the property
        :return: the bot's property of default value
        """
        default_pred = self.config.default_predicate
        default_property = self.config.properties.get("default")
        real_property = self.config.properties.get(name)
        return real_property or default_property or default_pred

    @abstractmethod
    def learn_category(self, category: str, global_: bool, user_id: str)\
            -> Logger:
        """
        Add (online) new knowledge to the bot's brain.

        (see <learn> and <learnf> tags for more precise description).

        :param category: string representation of category to add, the
            root element of underlying xml must be <category>
        :param global_: if True, add to brain used with all users, otherwise
            to the brain local for the given user
        :param user_id: user with whom the chatbot is chatting
        :return:  `Logger` instance with errors or warnings, if the logger
            has any errors, the `category` was not loaded
        """

    @abstractmethod
    def learn_aiml(self, filename: str) -> Logger:
        """
        Load .aiml file and store its contents in the (global) graphmaster.

        :param filename: name of the `.aiml` file
        :return: `Logger` instance with errors or warnings, if the logger
            has any errors, the `filename` file was not loaded
        """

    @abstractmethod
    def learn_aimlif(self, filename: str) -> Logger:
        """
        Load .aimlif file and store its contents in the (global) graphmaster.

        :param filename: name of the `.aimlif` file
        :return: `Logger` instance with errors or warnings, if the logger
            has any errors, the `filename` file was not loaded
        """

    @abstractmethod
    def vocabulary(self, user_id: str) -> int:
        """
        Find the number of distinct words stored as nodes in the bot's brain.

        The results are combined with global brain and brain for the
        specified user. Implements the <vocabulary> tag.

        :param user_id: the user for whom we should consider the local brain
        :return: number of distinct words
        """

    @abstractmethod
    def brain_size(self, user_id: str) -> int:
        """
        Find the number of categories stored in the brain.

        Combines the results with global brain and brain for the
        specified user. Implements the <size> tag.

        :param user_id: the user for whom we should consider the local brain
        :return: number of categories in the brain
        """
