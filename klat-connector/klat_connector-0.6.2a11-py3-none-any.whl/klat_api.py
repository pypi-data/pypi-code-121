# NEON AI (TM) SOFTWARE, Software Development Kit & Application Development System
#
# Copyright 2008-2021 Neongecko.com Inc. | All Rights Reserved
#
# Notice of License - Duplicating this Notice of License near the start of any file containing
# a derivative of this software is a condition of license for this software.
# Friendly Licensing:
# No charge, open source royalty free use of the Neon AI software source and object is offered for
# educational users, noncommercial enthusiasts, Public Benefit Corporations (and LLCs) and
# Social Purpose Corporations (and LLCs). Developers can contact developers@neon.ai
# For commercial licensing, distribution of derivative works or redistribution please contact licenses@neon.ai
# Distributed on an "AS IS” basis without warranties or conditions of any kind, either express or implied.
# Trademarks of Neongecko: Neon AI(TM), Neon Assist (TM), Neon Communicator(TM), Klat(TM)
# Authors: Guy Daniels, Daniel McKnight, Regina Bloomstine, Elon Gasper, Richard Leeds
#
# Specialized conversational reconveyance options from Conversation Processing Intelligence Corp.
# US Patents 2008-2021: US7424516, US20140161250, US20140177813, US8638908, US8068604, US8553852, US10530923, US10530924
# China Patent: CN102017585  -  Europe Patent: EU2156652  -  Patents Pending

import uuid
import time
import json


from threading import Event
from typing import Optional
from datetime import datetime

from . import SocketIOCompat
from .encryptor import generate_hash
from .logger import LOG
from .exceptions import *
from .klat_api_abc import KlatApiABC
from socketio import Client
from klat_connector.utils.html_utils import clean_html_entities


FIRST_SHOUT = "New API Conversation."


class KlatApi(KlatApiABC):
 
    def __init__(self, socket, dom="klattalk.com", init_nick=None):
        """
        Initializes a Klat connection to the passed socket. Initially connects as a guest user in the passed domain.
        :param socket: socketio.client Client socket connection to the Klat server
        :param dom: initial Klat domain to connect to
        """
        self._uid = str(uuid.uuid1())
        self._users = None
        self._nick = init_nick or ""
        self._title = None
        self._cid = None
        self._dom = dom
        self._log = None
        self._profile = None  # Populated on "nickname" or "mobile login return"
        self._devices = None  # Populated on "nickname"
        self._login = 0       # 0=in-progress 1=guest 2=logged in

        self._users_last_updated = 0
        self._users_list_cache = 2
        self._socket_id = None
        self._client = "api"
        self._get_users_timeout = 5

        # self._await_log = False
        self._await_log = Event()
        self._await_users_list = Event()
        self._await_change_conversation = Event()
        self._await_new_conversation = Event()
        self._await_login = Event()
        self._await_logout = Event()
        self._created_cid = None
        self._created_title = None
        self._created_needs_shout = False

        self.instance = str(round(time.time()))
        self.socket: Client = socket
        self.klat_ready = Event()
        self.klat_ready.clear()
        self._setup_listeners()

        if not self.socket.connected:
            raise ConnectionError
        self._start_connection()

        if not self.klat_ready.wait(30):
            LOG.error(f"Timed out waiting for Klat Ready!")
            self.socket.disconnect()
            raise KlatAPIError("Klat server connection not established!")

    @property
    def ready(self) -> bool:
        """
        Added for backwards-compat. Use klat_ready.wait() instead of polling ready
        :return:
        """
        LOG.warning(f"This method is depreciated! Use `self.klat_ready` event.")
        return self.klat_ready.is_set()

    @property
    def connected(self) -> bool:
        return self.socket.connected

    @property
    def chat_log(self) -> list:
        return self._log

    @property
    def nick(self) -> str:
        return self._nick

    @property
    def title(self) -> str:
        return self._title

    @property
    def logged_in(self) -> int:
        """
        Wraps self._login to return login status
        :return: 0 = Disconnected, 1 = Guest, 2 = User
        """
        return self._login

    @property
    def conversation_is_proctored(self) -> bool:
        """
        Determines if there is a Proctor in the current conversation
        :return: Boolean if there is a proctor in the current conversation
        """
        users = [u.lower() for u in self.conversation_users]
        if users and len(users) > 0:
            LOG.debug(users)
            return "proctor" in users
        else:
            LOG.warning(f"Error updating conversation users!! Proctored={self._dom == 'chatbotsforum.org'}")
            return self._dom == "chatbotsforum.org"

    @property
    def conversation_users(self) -> list:
        """
        Returns an updated list of users in the current conversation
        :return: list of nicks in the current conversation
        """
        if time.time() - self._users_last_updated > self._users_list_cache or not self._users:
            # 'get nicks for cid', cid
            self.socket.emit("get nicks for cid", self._cid)
            self._await_users_list.clear()
            if not self._await_users_list.wait(self._get_users_timeout):
                LOG.error(f'Missing response to users: {self._cid}, fallback to old value')

        if self._users != list(dict.fromkeys(self._users)):
            LOG.warning(f"Duplicates found in users: {self._users}")
            self._users = list(dict.fromkeys(self._users))
        return self._users

    def is_current_cid(self, cid: str) -> bool:
        """
        Checks if the passed cid is the current cid.
        :param cid: cid to check
        :return: True if cid is the current cid
        """
        return cid == self._cid

    # Exposed API Methods
    def send_shout(self, shout: str, cid: str = None, dom: str = None):
        """
        Shout into the current conversation or else passed dom/cid
        :param shout: text to shout
        :param cid: CID to send shout into (Private cid for @user shout)
        :param dom: Domain associated with cid
        """
        cookies = json.loads('{"ShareMyRecordings": 1}')
        dest_dom = dom or self._dom
        dest_cid = cid or self._cid

        try:
            self._send_shout(shout, dest_dom, dest_cid, cid, cookies)
        except ConnectionError:
            LOG.error(f"Socket disconnected skipping sending: {self.nick} - {shout}")
        except Exception as e:
            LOG.error(e)

    def search_shout(self, search: str, shout_context: int = 10, shout_time: int = 30):
        """
        Search for a shout with the given input
        :param search: input string (regex supported) to match
        :param shout_context: Number of contextual shouts to return (before or after)
        :param shout_time: Max seconds of context to provide (before or after)
        """
        # (search, num_context, max_time)
        self.socket.emit("search shouts by phrase", (search, shout_context, 1000*shout_time))

    def login_klat(self, user: str, password: str):
        """
        Login to klat.com with the passed username and password
        :param user: klat nick
        :param password: cleartext login password
        """

        if not self.klat_ready.wait(30):
            LOG.error(f"Timed out waiting for Klat Ready!")
            self.socket.disconnect()
            raise KlatAPIError("Klat server connection not established!")
        self._login = 0
        self._await_login.clear()
        hash_pass = generate_hash(password)
        self.socket.emit("check login", (self._nick, user, self._dom, hash_pass, None, self._cid, self._uid))
        if not self._await_login.wait(30):
            self.socket.disconnect()
            raise LoginError("Error in response to 'check login'")

    def logout_klat(self):
        """
        Log out of current account
        """
        # (nick, dom, color, cid, kinstance, col, page name)
        self.socket.emit("logout", (self._nick, self._dom, None, self._cid, self.instance, "col1", "1col"))
        self._await_logout.clear()
        if not self._await_logout.wait(30):
            self.socket.disconnect()
            raise LoginError("Error in response to 'logout'")

    def register_klat(self, username, password):
        """
        Register a new user
        """
        self._login = 0
        self._await_login.clear()
        self.socket.emit("save login", (username, self._dom, generate_hash(password), "rgb(0, 0, 0)", self._cid,
                                        str(self.instance), "col1", "1col", "1", "1", 1.0, "Google US English",
                                        "Joanna", "female", "en-us", "en-us", "en", 12, "imperial", "MDY", "Renton",
                                        "Washington", "United States", self._uid, None))
        if not self._await_login.wait(30):
            self.socket.disconnect()
            raise LoginError("Error in response to 'save login'")

    def change_domain(self, new_dom: str):
        """
        Change to a new conversation domain
        :param new_dom: domain to go to
        """
        # (whichWay, currentCid, domainToGoTo, doChangeDomain)
        if new_dom.lower() == "private":
            new_dom = "Private"
        else:
            new_dom = new_dom.lower()
        # TODO: verify domain is valid DM
        self._await_change_conversation.clear()
        self.socket.emit("change domain", ("this one", self._cid, new_dom))
        if not self._await_change_conversation.wait(30):
            self.socket.disconnect()
            raise ChangeConversationError(f"Change Domain Error! new_dom={new_dom}")
        if new_dom == "Private" and self._nick.lower() not in self._title.lower():
            self.socket.disconnect()
            raise ChangeConversationError(f"Invalid Private conversation joined! nick={self._nick}|title={self.title}")

    def change_conversation(self, new_cid: str, new_dom: str):
        """
        Change to a new conversation by cid
        :param new_cid: cid to go to
        :param new_dom: domain for new_cid
        """
        self._await_change_conversation.clear()
        # (whichWay, currentCid, domainToGoTo, doChangeDomain)
        self.socket.emit("change domain", ("conversation only", new_cid, new_dom))

        if not self._await_change_conversation.wait(30):
            self.socket.disconnect()
            raise ChangeConversationError(f"Change Conversation Error! new_dom={new_dom}|new_cid={new_cid}")

    def get_private_conversation(self, users: list) -> Optional[str]:
        """
        Helper function that wraps create_conversation and builds a title from a list of desired users.
        Private conversation is created if not exists and cid is returned.
        :param users: list of users to include in the private conversation
        :return: cid of created conversation
        """
        if self._nick not in users:
            LOG.info(f"adding creating user to conversation: {self._nick}")
            users.append(self._nick)
        title = f"!PRIVATE:{','.join(users)}"
        new_cid = self.create_conversation("Private", title)
        return new_cid

    def create_conversation(self, dom: str, title: str, goto: bool = False,
                            first_shout: str = FIRST_SHOUT) -> Optional[str]:
        """
        Creates a new Klat conversation with the given parameters
        :param dom: Domain for new conversation
        :param title: Title of new conversation
        :param goto: Flag switch to created conversation
        :param first_shout: First shout to send into new conversation
        :return: Created cid or null if failed
        """
        self._created_cid: Optional[str] = None
        self._await_new_conversation.clear()

        if title.startswith("!PRIVATE:") and dom != "Private":
            LOG.error(f"Attempt to create private conversation in dom={dom}")
            dom = "Private"

        # (domain, nick, cid, title, ImageURL, ArticleURL, msgFromNeon, PassHash, FirstShout, keychain)
        self.socket.emit("create conversation", (dom, self._nick, self._cid, title, "", "", None, "",
                                                 first_shout, None))

        if not self._await_new_conversation.wait(30):
            self.socket.disconnect()
            raise CreateConversationError(f"New conversation timed out! dom={dom}, title={title}")
        if self._created_cid:
            if self._created_needs_shout:
                self.send_shout(first_shout, self._created_cid, dom)
            if goto:
                self._title = self._created_title
                self.change_conversation(self._created_cid, dom)
        else:
            # TODO: Should this raise an exception? DM
            LOG.error(f"Error while creating {title} on {dom}")
        return self._created_cid

    def get_conversation_log(self, follows: int = 10, context: int = 20,
                             shouts: int = 50, age: int = 60000, last: int = 0):
        """
        Requests an update of the conversation history for the current conversation
        :param follows: Max number of followed conversations to get
        :param context: Max number of context shouts to get surrounding crossposts
        :param shouts: Max number of shouts to get
        :param age: Max age of shouts to get in seconds
        :param last: Millis time of oldest shout to get
        """
        self._log = None

        max_follows = str(follows)
        max_context = str(context)
        max_shouts = str(shouts)
        max_time = str(age)
        last_shout = last
        # self._await_log = True
        self._await_log.clear()
        # (myDomain, oldConversation, myConversation, myNick, myFollowsKey, myColumn, myMaxFollowedConversations,
        # myContextMax, myContextTime, nano, lastShout, numShouts, function(err){})
        self.socket.emit("get log", (self._dom, "", self._cid, self._nick, "", "col1",
                                     max_follows, max_context, max_time, self._client, last_shout, max_shouts))

        if not self._await_log.wait(30):
            self.socket.disconnect()
            raise KlatAPIError("No conversation log received from server!")

    # Handlers to be overridden
    def handle_incoming_shout(self, user: str, shout: str, cid: str, dom: str, timestamp: str):
        """
        This function should be overridden to handle incoming messages
        :param user: user associated with shout
        :param shout: user's shout
        :param cid: cid shout belongs to
        :param dom: domain conversation belongs to
        :param timestamp: time of incoming shout
        """
        pass

    def handle_login_return(self, status: int):
        """
        This function should be overridden to handle login return status
        :param status: non-success return code
        """
        pass

    def handle_search_results(self, kind: str, results: dict):
        """
        This function should be overridden to handle search results
        :param kind: elements searched (i.e. "shouts")
        :param results: dict of matched and contextual shouts by cid
        """
        pass

    def handle_socket_reconnected(self):
        """
        This function should be overridden to handle a server socket reconnection
        """
        pass

    # Socket Listeners
    def _on_connect(self):
        """
        Handler for socket connection
        """
        LOG.info("Chat Server Connected")
        if self._login != 0:
            # Handle reconnections here
            self.handle_socket_reconnected()
            self._start_connection()

    @staticmethod
    def _on_disconnect():
        """
        Handler for socket disconnection
        """
        # self.connected = False
        LOG.warning("Chat Server Socket Disconnected!")

    @staticmethod
    def _on_reconnect():
        """
        Handler for socket reconnection
        """
        # self.connected = True
        LOG.warning("SocketIO Reconnected")

    def _on_conversation_list(self, *args):
        """
        Handler for "conversation list". Emits "nickname"
        :param args: Socket Arguments
        """
        self._socket_id = args[2]
        conversations = args[0][0]  # JsonArray of JsonObjects
        new_conversation = self._parse_conversations_list(conversations)
        c_nick = self._nick or new_conversation["cNick"]
        l_uname = self._nick or new_conversation["lUname"]
        new_title = new_conversation["title"]
        # (myCNick, luname, ldom, myConversation, userTitle, myFollowsKey, myColumn, myKinstance, myPageName,
        # myTtsLanguage, mySecondTtsLanguage, mySttLanguage, nano, uid, function...
        self.socket.emit("nickname",
                         (c_nick, l_uname, self._dom, self._cid, new_title, "", "col1", float(self.instance),
                          "1col", "en-us", "en-us", "en", self._client, self._uid, None))

    def _on_nickname(self, *args):
        """
        Handler for "nickname". After this, _profile is populated and we can send/receive messages
        :param args: Socket Arguments
        :return:
        """
        self._nick = args[0]
        self._devices = args[1]
        self._profile = args[2]
        LOG.info(f"Logged in as {self._nick}")
        self._login = 1
        self._await_logout.set()
        self.klat_ready.set()

    def _on_user_message(self, *args):
        """
        Handler for "user message" (incoming shouts)
        :param args: Socket Arguments
        """
        LOG.debug(args)
        shout = clean_html_entities(args[0])
        user = args[1].split('#', 1)[0]
        s_cid = str(args[2])
        s_dom = args[5]
        s_time = round(int(args[3]) / 1000)
        p_time = datetime.fromtimestamp(s_time).strftime("%I:%M:%S %p")
        self.handle_incoming_shout(user, shout, s_cid, s_dom, p_time)

    def _on_login_return(self, *args):
        """
        Handler for "mobile login return". This is where nick is updated
        :param args: Socket Arguments
        """
        self._users = None  # Clear users to force checking with server
        LOG.debug(len(args))
        login_status = args[0]
        if login_status == 0:
            # Successful Login
            self._nick = args[1]
            if not self._profile:
                LOG.error("Profile not defined at login return!")
                self._profile = {}
            self._profile = {"display_nick": args[1],
                             "color": "",
                             "avatar_url": args[4],
                             "pass": "",
                             "mail": args[3],
                             "login": time.time(),
                             "timezone": None,
                             "ip": self._profile.get("ip", "0.0.0.0"),
                             "speech_rate": self._profile.get("speech_rate", "1.0"),
                             "speech_pitch": self._profile.get("speech_pitch", "1.0"),
                             "volume": float(args[33] or 0.0),
                             "speech_voice": args[11],
                             "ai_speech_voice": args[12],
                             "time_format": args[17],
                             "date_format": args[18],
                             "unit_measure": args[19],
                             "stt_language": args[16],
                             "tts_language": args[14],
                             "tts_secondary_language": args[15],
                             "tts_voice_gender": self._profile.get("tts_voice_gender", "female")}

            # Goto new conversation
            if args[27]:
                LOG.info("Create new Private!")
            elif self._dom == "Private":
                new_cid = str(args[26])
                self._cid = new_cid
            self._login = 2
        elif login_status == 777:
            self.logout_klat()
            self._login = -1
            self._nick = ''
        elif login_status == "mock":
            self._profile = {}
            self._nick = args[1]
            self._login = 2  # Logged in on mock server
            login_status = 0
        else:
            self._login = 1
            self._await_logout.set()
        LOG.info(f"Logged in as: {self._nick}")
        self._await_login.set()
        self.handle_login_return(login_status)

    def _on_new_domain(self, *args):
        """
        Handler for "new domain". This is where dom and cid are updated
        :param args: Socket Arguments
        """
        LOG.debug(args)
        self._cid = str(args[0])
        self._users = args[1] or []
        if self._nick not in self._users:
            LOG.warning("Nick not included in new conversation!")
            self._users.append(self._nick)

        self._users_last_updated = time.time()
        data = args[2]
        self._dom = data.get("dom")
        self._title = data.get("title")
        LOG.info(f">>>Got new cid: {self._cid} with title: {self._title}")
        self._await_change_conversation.set()

    def _on_chat_log(self, *args):
        """
        Handler for "chat log" Populates shout history for the current conversation
        :param args: Socket Arguments
        """
        history = args[0]
        users = args[1]
        self._log = history or []
        self._users = users
        if self._nick not in users:
            LOG.warning("Nick not included in new conversation!")
            self._users.append(self._nick)
        # self._await_log = False
        self._await_log.set()

    def _on_log_out(self, *args):
        """
        Handler for "log out successful"
        :param args: Socket Arguments
        """
        self._users = None
        LOG.debug(args)
        self._login = 0
        self._nick = ''
        if self._dom == "Private":
            self._cid = None
        self._start_connection()

    def _on_search_shouts_by_phrase_return(self, *args):
        """
        Handler for "search shouts by phrase return"
        :param args: Socket Arguments
        """
        LOG.debug(args)
        results = dict()
        for key, val in dict(args[0]).items():
            new_key = key.split(":")[0]
            if new_key in results.keys():
                results[new_key].append(val)
            else:
                results[new_key] = [val]
        self.handle_search_results("shouts", results)

    def _on_nicks_list(self, *args):
        """
        Handler for "new nick list"
        :param args: Socket Arguments
        """
        # if self._users:
        #     LOG.warning(f"users not empty, this probably came late!")
        LOG.info(f"Got new users: {args[1]}")
        self._users_last_updated = time.time()
        self._users = args[1]
        self._await_users_list.set()

    def _on_save_login_return(self, *args):
        """
        Handler for "save login return"
        :param args: Socket Arguments
        """
        self._users = None  # Clear users to force checking with server
        register_status = args[2]
        if register_status == "Name already exists.":
            success = False
        elif register_status == "Name cannot contain non-alphanumeric characters or reserved words.":
            success = False
        elif register_status == "Save login successful.":
            success = True
        else:
            success = False

        confirmed_nick = args[1]
        if success:
            LOG.info(f"Logged in as {confirmed_nick}")
            self._nick = confirmed_nick
            if self._dom == "Private":
                self._cid = None
                self.change_domain("Private")
            self._login = 2
        else:
            self._login = 1
        self._await_login.set()

    def _on_create_conversation_return(self, *args):
        """
        Handler for "create conversation return
        :param args: Socket Arguments
        """
        ret_cid: str = str(args[0])
        need_shout = False
        if ret_cid.startswith("Title exists - "):
            new_cid = ret_cid.split("-", 1)[1].strip()
            new_title: str = args[1]
            LOG.info(f"Cid exists: {ret_cid}")

        elif ret_cid.startswith("Cannot start non-private"):
            LOG.error(ret_cid)
            new_cid = None
            new_title = ""
        else:
            new_cid = ret_cid
            new_dom: str = args[3]
            new_title: str = args[4]
            # hash_pass: str = args[6]
            LOG.info(f"Created cid: {new_cid} on {new_dom}")
            need_shout = True

        self._created_cid = new_cid
        self._created_title = new_title
        self._created_needs_shout = need_shout
        self._await_new_conversation.set()

    # Internal Functions
    def _parse_conversations_list(self, conversations_list: dict):
        """
        Called by _on_conversation_list to parse returned JSON object and collect new conversation data
        :param conversations_list: conversation data
        :return: current conversation data
        """
        dom_data = conversations_list.get("row")
        new_dom = dom_data.get("dom")
        new_title = dom_data.get("title")
        new_cid = str(dom_data.get("cid", conversations_list.get("cid", [""])[0]))
        self._cid = new_cid
        self._dom = new_dom
        self._title = new_title

        c_nick = self._nick or ""
        if new_dom == "Private":
            l_uname = "Private:User"
        else:
            l_uname = "klat:User"

        return {"cNick": c_nick,
                "lUname": l_uname,
                "title": new_title}

    def _send_shout(self, shout: str, dest_dom: str, dest_cid: str, orig_cid: str, cookies: json):
        """
        Internal function that sends a shout into the current conversation and throws an exception if not connected
        :param shout: text to shout
        :param dest_dom: Destination domain for the shout
        :param dest_cid: Destination cid for the shout
        :param orig_cid: CID the shout originated from
        :param cookies: JSON object associated with this instance
        """

        if not self.socket.connected:
            raise ConnectionError(f"Socket disconnected skipping sending: {self.nick} - {shout}")
        else:
            # (msg, dom, cid, img, video, mode, imgData, showAnswers, audioBlobs, audioFileName, sttLanguage,
            # ttsLanguage, ttsSecondLanguage, ttsGender, needsTranslation, cidForLink, cookies, name, fn)
            self.socket.emit("user message", (shout, dest_dom, dest_cid, "", "", self._client, "", 0, None, False,
                                              self._profile.get("stt_language", "en"),
                                              self._profile.get("tts_language", "en-US"),
                                              self._profile.get("tts_secondary_language"), "male",
                                              self._profile.get("stt_language", "en") != "en", orig_cid,
                                              cookies, False, None, False, False, False))

    def _start_connection(self):
        """
        Initializes a new connection to the Klat server
        """
        nick = self._nick
        cid = self._cid or ""
        domain = self._dom or "Private"
        welcome_message = ""
        # (pCid, cookieCid, mode, dom, nick, tab, hash, url, klatGuid, pageName, column, kinstance, allCookies,
        # nano, welcomeMessage, fn)
        self.socket.emit("get conversation list 2", (cid, "", "init", domain, nick, "1", "", "",
                                                     self.instance, "1col", "col1", self.instance, "", self._client,
                                                     welcome_message))

    def _stop_connection(self):
        LOG.info('Connection stopped')

    def _setup_listeners(self):
        """
        Starts all Klat event listeners
        """
        self.socket.on("connect", self._on_connect)
        self.socket.on("disconnect", self._on_disconnect)
        self.socket.on("reconnect", self._on_reconnect)
        self.socket.on("conversation list", self._on_conversation_list)
        self.socket.on("nickname", self._on_nickname)
        self.socket.on("mobile user message", self._on_user_message)
        self.socket.on("mobile login return", self._on_login_return)
        self.socket.on("new domain", self._on_new_domain)
        self.socket.on("chat log", self._on_chat_log)
        self.socket.on("log out successful", self._on_log_out)
        self.socket.on("search shouts by phrase return", self._on_search_shouts_by_phrase_return)
        self.socket.on("new nick list", self._on_nicks_list)
        self.socket.on("save login return", self._on_save_login_return)
        self.socket.on("create conversation return", self._on_create_conversation_return)
        if isinstance(self.socket, SocketIOCompat):
            self.socket.run_forever()
