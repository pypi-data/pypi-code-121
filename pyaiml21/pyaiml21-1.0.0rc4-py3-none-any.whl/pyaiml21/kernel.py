"""Kernel - the backwards compatible implementation of the interpreter."""
from typing import Optional, Dict
from .chatbot import Bot


class Kernel(Bot):
    """
    Backwards compatible way to work with the interpreter.

    This class represents the whole interpreter, keeps the track of a bot
    and loading and manipulation with its files, configuration, etc.

    Note that some methods are missing, or have changed type signature.
    """

    DEFAULT_USED_ID = "default"

    def loadBrain(self, brain_file: str) -> None:
        """
        Attempt to load the brain global for all users from the specified file.

        Does not load configuration files, nor the custom tags.

        :param brain_file: filename from which to load the brain
        """
        self.gm.load(brain_file)

    def saveBrain(self, filename: str) -> None:
        """
        Store the global brain into the specified file.

        Does not save configuration files, nor the custom tags.

        :param filename: filename to save the brain into
        """
        self.gm.dump(filename)

    def resetBrain(self) -> None:
        """
        Reset bot's brain.

        Remove the content of bot's brain, equivalent to starting
        a new instance of the bot with the same name.
        """
        self.gm.root = self.gm.root.__class__()

    def setPredicate(self, name: str, value: str,
                     sessionID: Optional[str] = None) -> None:
        """
        Set the corresponding _predicate.

        :param name: name of the _predicate to set
        :param value: desired _predicate value
        :param sessionID: userID / sessionID to set _predicate for; or None
            to set global bot's _predicate
        """
        if not sessionID:
            sessionID = self.DEFAULT_USED_ID
            if sessionID not in self.sessions:
                self.init_new_user(sessionID)
        if sessionID not in self.sessions:
            raise ValueError("Unknown sessionID")
        self.sessions[sessionID].predicates[name] = value

    def getPredicate(self, name: str, sessionID: Optional[str] = None) -> str:
        """
        Return bot the specified bot's property.

        :param name: name of the property
        :param sessionID: id of the session
        :return: property value or empty string of not set
        """
        if sessionID is None:
            sessionID = self.DEFAULT_USED_ID
        if sessionID not in self.sessions:
            raise ValueError("Unknown session id")
        return self.sessions[sessionID].predicates.get(name, "")

    def setBotPredicate(self, name: str, value: str) -> None:
        """
        Set the corresponding bot property to the value.

        :param name: name of the property
        :param value: desired value
        """
        self.config.properties[name] = value

    def getBotPredicate(self, name: str) -> Optional[str]:
        """
        Get the corresponding bot property.

        :param name: name of the property
        """
        res: Optional[str] = self.config.properties.get(name)
        return res

    def getSessionData(self, sessionID: Optional[str]) -> Dict[str, str]:
        """
        Return a copy of session predicates.

        :param sessionID: id of the session
        :return: session predicates or empty dict if session is not found
        """
        if sessionID is None:
            sessionID = self.DEFAULT_USED_ID
        if sessionID not in self.sessions:
            raise ValueError("Unknown session id")
        return dict(self.sessions[sessionID].predicates)

    def learn(self, filename: str) -> None:
        """
        Load and learn content of the given aiml file.

        :param filename: .aiml or .aimlif with categories to learn
        """
        self.learn_aiml(filename)
