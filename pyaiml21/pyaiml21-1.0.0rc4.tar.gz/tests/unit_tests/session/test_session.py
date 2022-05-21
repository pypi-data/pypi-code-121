import pytest
from pyaiml21 import session
from pyaiml21.session import Session
from pyaiml21.botconfig import BotConfig



def test_bot_replies():
    bc = BotConfig()
    user = "1"
    session = Session(user, bc)

    session.add_bot_reply(["hi", "howdy", "hello 1", "2"])
    session.add_bot_reply(["1"])
    session.add_bot_reply(["a", "b"])

    assert session.get_bot_reply(0) == ["a", "b"]
    assert session.get_bot_reply(1) == ["1"]
    assert session.get_bot_reply(3) == []


def test_user_query():
    bc = BotConfig()
    user = "1"
    session = Session(user, bc)

    session.add_user_query(["a", "b"])
    session.add_user_query(["1"])

    assert session.get_bot_reply(0) == []
    assert session.get_user_query(0) == ["1"]
    assert session.get_user_query(1) == ["a", "b"]
    assert session.get_user_query(5) == []

    session = Session(user, bc, 1)
    session.add_user_query(["a"])
    session.add_user_query(["b"])
    assert session.get_user_query(1) == []
    assert session.get_user_query(0) == ["b"]
