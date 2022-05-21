"""The chatbot-client session."""
from typing import Optional, List

from pyaiml21.botconfig import Predicates, BotConfig
from pyaiml21.graphmaster import GraphMaster
from .bounded_list import BoundedList


class Session:
    """
    Represents chat session between a chatbot and an user.

    This class keeps track of the chat history, chat predicates and
    the graphmaster for this particular user.
    """

    def __init__(
        self, user_id: str,
        bc: BotConfig,
        max_history: Optional[int] = None
    ):
        """
        Create a chat session.

        :param user_id: id of the user chatting
        :param bc: configuration of the bot the user is chatting to
        :param max_history: max size of history to keep track of
        """
        self.user_id = user_id
        """id of the user from this session"""
        self.max_history_length: Optional[int] = max_history
        """max length of the history to keep track of"""
        self._user_queries: BoundedList[List[str]] = BoundedList(max_history)
        self._bot_replies: BoundedList[List[str]] = BoundedList(max_history)
        self.predicates = Predicates()
        self.gm = GraphMaster(bc)

    def add_bot_reply(self, reply: List[str]):
        """Add bot reply (list of sentences) to the session history."""
        self._bot_replies.add(reply)

    def get_bot_reply(self, index: int) -> List[str]:
        """
        Find `index`-th bot's reply.

        Return `index`-th bot reply as a list of sentences, or empty
        list, if we don't know the reply (don't have enough replies or
        `index` is more than `max_history_length`.

        :param index: index of the reply to get, 0 for newest
        :return: the reply consisting of the sentences
        """
        return self._bot_replies[index] or []

    def add_user_query(self, query: List[str]) -> None:
        """
        Add user query to th session history.

        :param query: list of sentences
        """
        self._user_queries.add(query)

    def get_user_query(self, index: int) -> List[str]:
        """
        Find `index`-th user query.

        Return `index`-th user query as a list of sentences, or empty
        list, if we don't know the query (don't have enough queries or
        `index` is more than `max_history_length`.

        :param index: index of the query to get, 0 for newest
        :return: the query consisting of the sentences
        """
        return self._user_queries[index] or []
