"""
AIML chatbot.

The main entrypoint to work with the interpreter.
"""
from typing import Iterable, List, Mapping, Type, Dict, Any, Optional, Set, \
    Tuple
import pyaiml21.stdlib as std
from pyaiml21.ast import Node, Category
from pyaiml21.bot import Bot as ABot
from pyaiml21.exceptions import AIMLError
from pyaiml21.graphmaster import GraphMaster, Pattern, StarBindings
from pyaiml21.interpreter import Interpreter, Debugger, AIMLEvalFun
from pyaiml21.parser import AIMLParser, Logger, TagSyntaxCheckerFn
from pyaiml21.session import Session
from pyaiml21.utils import normalize_user_input, split_sentences


class Bot(ABot):
    """
    Represents an AIML chatbot.

    The `Bot` is the main entity and is capable of responding to the user's
    inputs, managing user sessions and loading AIML contents.

    This class represents the main entrypoint to work with `pyaiml21`
    interpreter.
    """

    def __init__(self, gm_cls: Type[GraphMaster] = GraphMaster,
                 *args, **kwargs):
        """
        Create the chatbot.

        :param gm_cls: class of graphmaster to use to create the bot's brain
        :param *args: passed to `gm_cls` initialization call
        :param **kwargs: passed to the graphmaster initialization call
        """
        super().__init__()
        self.gm = gm_cls(self.config, *args, **kwargs)
        """Bot's 'brain' - the graphmaster global for all users."""
        self.sessions: Dict[str, Session] = dict()
        """All bot-user sessions of this bot."""
        self._eval_tags: Dict[str, Any] = dict()
        self._parse_tags: Dict[str, Any] = dict()
        self._load_std_features()
        self.normalize_fn = normalize_user_input
        """Remove punctuation and split into sentences and each to words."""

    def add_properties(self, props: Mapping[str, str]) -> None:
        """
        Add properties to the bot.

        :param props: dictionary with bot's properties
        """
        self.config.properties.update(props)

    def add_substitutions(self, tag: str, subs: Mapping[str, str]) -> None:
        """
        Update the substitutions of the bot.

        :param tag: name of the tag fot substitutions. e.g. `normalize`,
            `denormalize`, `gender`, `person`, `person2`
        :param subs: the substitutions
        """
        _tag2subs = {
            "normalize": self.config.normalize,
            "denormalize": self.config.denormalize,
            "gender": self.config.gender,
            "person": self.config.person,
            "person2": self.config.person2
        }
        s = _tag2subs.get(tag)
        if s is None:
            raise ValueError("Unknown tag name " + tag)
        for k, val in subs.items():
            s[k] = val

    def load_patterns(self, patterns: Iterable[Pattern]) -> None:
        """
        Learn pattern tags.

        After running this method, the bot will understand
        and be able to parse and match given `pattern`
        within its graphmasters.

        :param patterns: a list of objects representing <pattern> nodes
        """
        for pattern in patterns:
            self.gm.add_pattern_tag(pattern)
            for session in self.sessions.values():
                session.gm.add_pattern_tag(pattern)

    def load_tags(self, parse_tags: Dict[str, TagSyntaxCheckerFn],
                  eval_tags: Dict[str, AIMLEvalFun],
                  allow_different: bool = False) -> None:
        """
        Learn <template> tags.

        By default, check that the same tags are in both dictionaries,
        you can override this behaviour by setting `allow_different` flag.

        :param parse_tags: dictionary mapping from tag name to the function
            that parses the tag
        :param eval_tags: mapping from name of tag to the function that
            evaluates the tag
        :param allow_different: skip the check that both dictionaries
            contains the same tags
        """
        if not allow_different and parse_tags.keys() != eval_tags.keys():
            raise ValueError("Mismatched tags")
        self._eval_tags.update(eval_tags)
        self._parse_tags.update(parse_tags)

    def load_set(self, name: str, s: Set[str]) -> None:
        """
        Learn and store AIML set `s`.

        The elements of the set `s` are expected to be in the uppercase.
        """
        self.config.sets[name] = s

    def load_map(self, name: str, m: Mapping[str, str]) -> None:
        """
        Learn and store AIML map `m`.

        The keys of the map `m` are expected to be in the uppercase.
        """
        self.config.maps[name] = m

    def _load_std_features(self):
        """Learn all standard tags, sets and maps."""
        self.load_patterns(std.PATTERNS)
        self.load_tags(std.TEMPLATE_PARSER, std.TEMPLATE_EVAL, True)
        for name, s in std.STD_SETS.items():
            self.load_set(name, s)
        for name, m in std.STD_MAPS.items():
            self.load_map(name, m)

    def get_predicate(self, name: str, user_id: str) -> str:
        """
        Find and return the value of a bot's _predicate.

        :param name: name of the _predicate
        :param user_id: current user we are chatting with
        :return: the _predicate value or `self.config.default_predicate`
        """
        default = self.config.default_predicate
        default = self.config.predicate_defaults.get(name, default)
        session = self.sessions[user_id]
        if session is None or name not in session.predicates:
            return default
        return session.predicates[name]

    def get_session(self, user_id: str) -> Optional[Session]:
        """Access arbitrary bot-user session."""
        return self.sessions.get(user_id)

    def _learn_categories(self, categories: Iterable[Category],
                          logger: Logger) -> Logger:
        """Learn a set of categories."""
        for c in categories:
            self.gm.validate(c, logger)
        if logger.has_errors():
            return logger
        for c in categories:
            self.gm.save(c)
        return logger

    def learn_aiml(self, aiml_file: str) -> Logger:
        """
        Load .aiml file and store its contents in the (global) graphmaster.

        :param aiml_file: name of the `.aiml` file
        :return: `Logger` instance with errors or warnings, if the logger
            has any errors, the `filename` file was not loaded
        """
        parser = AIMLParser()
        parser.known_tags = self._parse_tags
        cats, logger = parser.parse_aiml_file(aiml_file)
        if cats is None or logger.has_errors():
            return logger
        return self._learn_categories(cats, logger)

    def learn_aimlif(self, aimlif_file: str) -> Logger:
        """
        Load .aimlif file and store its contents in the (global) graphmaster.

        :param aimlif_file: name of the `.aimlif` file
        :return: `Logger` instance with errors or warnings, if the logger
            has any errors, the `filename` file was not loaded
        """
        parser = AIMLParser()
        parser.known_tags = self._parse_tags
        cats, logger = parser.parse_aimlif_file(aimlif_file)
        if cats is None or logger.has_errors():
            return logger
        return self._learn_categories(cats, logger)

    def learn_category(self, category: str, global_: bool, user_id: str) \
            -> Logger:
        """
        Learn category online, during the evaluation of the response.

        :param category: category to learn, root element is <category>
        :param global_: if True, learn and save to file global for all users,
            otherwise only for user with `user_id`
        :param user_id: id of the user we are chatting with
        :returns: True on success (parsing reported 0 errors, user exists)
        """
        parser = AIMLParser()
        parser.known_tags = self._parse_tags
        try:
            cat, log = parser.parse_category_aiml(category)
            if cat is None or log.has_errors():
                return log
            gm = self.gm if global_ else self.sessions[user_id].gm
            gm.validate(cat, log)
            if log.has_errors():
                return log
            gm.save(cat)
            # local files are stored online only
            if not global_:
                return log
            # globals we need to save in the file
            DATA = [category, "</aiml>"]
            # create the file if not exists
            with open(self.config.learnf_file, "a+"):
                ...
            # write the data
            with open(self.config.learnf_file, "r+", encoding="utf-8") as f:
                lines = f.read().splitlines()
                if not lines:
                    lines = ["<aiml>"]
                else:
                    lines.pop()
                lines.extend(DATA)
                f.seek(0)
                f.write("\n".join(lines))
                f.truncate()
                print(DATA, "===============")
            return log
        except Exception as e:
            raise AIMLError() from e

    def vocabulary(self, user_id: str) -> int:
        """
        Find the number of distinct words stored as nodes in the bot's brain.

        The results are combined with global brain and brain for the
        specified user. Implements the <vocabulary> tag.

        :param user_id: the user for whom we should consider the local brain
        :return: number of distinct words
        """
        vocab = self.gm.vocabulary()
        session = self.get_session(user_id)
        if session is not None:
            vocab |= session.gm.vocabulary()
        return len(vocab)

    def brain_size(self, user_id: str) -> int:
        """
        Find the number of categories stored in the brain.

        Combines the results with global brain and brain for the
        specified user. Implements the <size> tag.

        :param user_id: the user for whom we should consider the local brain
        :return: number of categories in the brain
        """
        sz = self.gm.size()
        session = self.get_session(user_id)
        if session is not None:
            sz += session.gm.size()
        return sz

    def init_new_user(self, user_id: str) -> Session:
        """Create a chat session for a new user, user must be a new user."""
        assert user_id not in self.sessions
        session = Session(user_id, self.config)
        for p in self.gm._known_patterns:
            session.gm.add_pattern_tag(p)
        self.sessions[user_id] = session
        return session

    def preprocess(self, text) -> List[str]:
        """
        Normalize the text fed to the graphmaster.

        Expand the abbreviations, remove punctuation and split the text
        into sentences.

        :param text: text to be normalized
        :return: normalized sentences
        """
        subbed = self.config.normalize.sub(text)
        words = self.normalize_fn(subbed) or [[""]]
        sentences = [" ".join(x) for x in words]
        return sentences

    def search_brain(self, user_id: str, sentence: str) \
            -> Optional[Tuple[Node, StarBindings, bool]]:
        """
        Search the bot's brain and return the appropriate template node.

        :param user_id: user from the bot-client conversation
        :param sentence: normalized sentence for which to find the template
        :return: None if no match was found, else triple with template node,
            matched stars and flag signalizing whether the match was exact
            using $WORD
        """
        # prepare the session
        session = self.get_session(user_id)
        if not session:
            raise AIMLError("Missing chatbot-user session")

        # preprocess that and topic
        that = (session.get_bot_reply(0) or ["UNKNOWN"])[-1]
        that = self.preprocess(that)[0]  # take the last response
        topic = session.predicates.get("topic", "UNKNOWN")
        topic = self.preprocess(topic)[0]

        # find the matches
        global_match = self.gm.match(sentence, that, topic)
        local_match = session.gm.match(sentence, that, topic)

        # find the best match and return
        if local_match is None and global_match is None:
            return None
        if local_match is None:
            best = global_match
        elif global_match is None:
            best = local_match
        else:
            best = local_match \
                if local_match[2] >= global_match[2] \
                else global_match
        assert best is not None
        node, stars, order = best
        is_exact = order[0] == std.EXACT_MATCH_SCORE
        return node, stars, is_exact

    def respond(self, input_: str, user_id: str, debug: bool = False) -> str:
        """
        Search graphmaster and return the reply to `input_`.

        :param user_id: user id for whom to search
        :param input_: user input to match
        :param debug: if true, use interactive debugger `Debugger` to find
            the answer
        :return: the bot's reply
        """
        session = self.get_session(user_id)
        if session is None:
            session = self.init_new_user(user_id)

        queries = self.preprocess(input_)
        responses: List[str] = []
        try:
            for q in queries:
                interpreter: Interpreter
                if debug:
                    interpreter = Debugger(self, session)
                    interpreter.stop_on_first()
                else:
                    interpreter = Interpreter(self, session)
                interpreter.known_tags = self._eval_tags
                reply = interpreter.call(q).strip()  # remove spaces around
                responses.append(reply)
        except Exception:
            responses = [self.config.default_answer]

        # as bot might respond with multiple sentences, split them here
        result = " ".join(responses)
        session.add_user_query(queries)  # from oldest to newest
        responses = list(map(str.strip, split_sentences(result)))
        session.add_bot_reply(responses)
        return result
