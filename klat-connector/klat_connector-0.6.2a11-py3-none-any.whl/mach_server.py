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

import logging

from multiprocessing import Process
from time import time
from socketio import Server, WSGIApp
from eventlet import wsgi, listen

from klat_connector.logger import LOG


class MachKlatServer:
    def __init__(self, port: int = 8888):
        logging.getLogger("engineio").setLevel(logging.WARNING)
        logging.getLogger("socketio").setLevel(logging.WARNING)
        self.server = self._create_local_server()

        self._socket_users = dict()
        self._domain_to_cid = dict()
        self._p_title_to_cid = dict()
        self._cid_nicks = dict()

        self._set_server_event_listeners()
        self.t = Process(target=self._start_server_listener, args=(self.server, port), daemon=True)
        self.t.start()
        LOG.debug("Mock Server Ready")

    def shutdown_server(self):
        """
        Terminates the server thread to end this process
        """
        self.t.terminate()

    @staticmethod
    def _start_server_listener(sio_server: Server, port: int):
        wsgi.server(listen(('0.0.0.0', port)), WSGIApp(sio_server))

    @staticmethod
    def _create_local_server() -> Server:
        """
        Creates a socketIO server
        :return: socketIO Server
        """
        return Server(async_mode="eventlet")

    @staticmethod
    def _generate_unique_nick() -> str:
        """
        Generates a unique nickname for a user
        :return: Random generated username
        """
        return f"guest{round(time())}"

    def _get_domain_cid(self, dom: str, title: str = None) -> str:
        """
        Get a cid associated with a given domain
        :param dom: domain requested
        :param title: optional title for Private domain use
        :return: cid
        """
        if dom == "Private":
            if title not in self._p_title_to_cid.keys():
                cid = str(round(time() * 1000))[5:]
                self._p_title_to_cid[title] = cid
            return self._p_title_to_cid.get(title)
        else:
            if not self._domain_to_cid.get(dom, None):
                self._domain_to_cid[dom] = str(round(time() * 1000))[5:]
            return self._domain_to_cid.get(dom)

    def _change_socket_nick(self, old_nick: str, new_nick: str, cid: str, sid: str):
        """
        Update internal references when a socket nick changes
        :param old_nick: old nick associated with socket
        :param new_nick: new nick associated with socket
        :param cid: cid socket is connected to
        :param sid: socketID associated with request
        :return:
        """
        new_nick = new_nick.lower()
        self._socket_users[sid] = new_nick
        self.server.enter_room(sid, new_nick)
        if not self._cid_nicks.get(cid):
            self._cid_nicks[cid] = list()
        if old_nick in self._cid_nicks[cid]:
            self._cid_nicks[cid].remove(old_nick)
        self._cid_nicks[cid].append(new_nick)

    def _get_nicks_for_cid(self, sid, *data):
        """
        Handle a request for nicks in the current cid
        :param sid: SocketID associated with request
        :param data: (cid requested)
        """
        # LOG.debug(f"{sid} get nicks")
        try:
            users = self._cid_nicks.get(data[0])
            LOG.debug(f"Got users: {users}")
            self.server.emit("new nick list", (None, users), sid)
        except Exception as e:
            LOG.error(e)

    def _check_login(self, sid, *data):
        """
        Handle a login request
        :param sid: SocketID associated with request
        :param data: (curr_nick, login_nick, curr_dom, hash_pass, ?, curr_cid, dev_uid)
        """
        LOG.info(f"{data[0]} Check Login as {data[1]}")
        old_nick = data[0]
        nick = data[1]
        cid = data[5]
        self._change_socket_nick(old_nick, nick, cid, sid)
        self.server.emit("mobile login return", ("mock", nick), sid)

    def _logout(self, sid, *data):
        """
        Handle a logout request
        :param sid: SocketID associated with request
        :param data: (nick, domain, ?, cid, instanceID, col#, #col)
        """
        LOG.info(f"{sid} Logout")
        cid = data[3]
        old_nick = data[0]
        new_nick = self._generate_unique_nick()
        self._change_socket_nick(old_nick, new_nick, cid, sid)
        self.server.emit("log out successful", (), sid)

    def _get_conversation_list(self, sid, *data):
        """
        Handle a request for conversation list
        :param sid: SocketID associated with request
        :param data: (pCid, cookieCid, mode, dom, nick, tab, hash, url, klatGuid, pageName, column, kinstance,
            allCookies, nano, welcomeMessage, fn)
        """
        LOG.info(f"{sid} Conversation List")
        cid = self._get_domain_cid(data[3])
        self.server.enter_room(sid, cid)
        conversations = [{"row": {"dom": data[3], "title": "Mock Server Testing", "cid": cid}}]
        self.server.emit("conversation list", (conversations, None, sid), sid)

    def _nickname(self, sid, *data):
        """
        Handle a request for nickname
        :param sid: SocketID associated with request
        :param data: (myCNick, luname, ldom, myConversation, userTitle, myFollowsKey, myColumn, myKinstance, myPageName,
            myTtsLanguage, mySecondTtsLanguage, mySttLanguage, nano, uid, function)
        """
        LOG.debug(f"{sid} Nickname")
        LOG.debug(data)
        nick = self._generate_unique_nick()
        self._socket_users[sid] = nick
        LOG.info(self._socket_users)
        devices = None
        profile = {}
        self.server.emit("nickname", (nick, devices, profile), sid)

    def _user_message(self, sid, *data):
        """
        Handle an incoming user message
        :param sid: SocketID associated with request
        :param data: (msg, dom, cid, img, video, mode, imgData, showAnswers, audioBlobs, audioFileName, sttLanguage,
            ttsLanguage, ttsSecondLanguage, ttsGender, needsTranslation, cidForLink, cookies, name, fn)
        """
        LOG.debug(f"{data[2]} | {data[0]}")
        shout = data[0]
        user = self._socket_users.get(sid, "UNDEF")
        cid = str(data[2])
        dom = data[1]
        millis_time = round(time() * 1000)
        # for socket in self._socket_users.keys():
        #     if socket != sid:
        # for socket in self._socket_users.keys():
        #     LOG.debug(f"{self._socket_users[socket]} is in: {self.server.rooms(socket)}")
        if shout.startswith("@"):
            username = shout.split(" ", 1)[0].lstrip("@").lower()
            LOG.info(f"Sending shout to room: {username}")

            for sid in self._socket_users.keys():
                rooms = self.server.rooms(sid)
                if username in rooms:
                    LOG.info(f"DM to {username} | {sid}")
            self.server.emit("mobile user message", (shout, user, cid, millis_time, None, dom), room=username)
        else:
            self.server.emit("mobile user message", (shout, user, cid, millis_time, None, dom), room=cid)

    def _create_conversation(self, sid, *data):
        """
        Handle a request to create a conversation
        :param sid: SocketID associated with request
        :param data: (domain, nick, cid, title, ImageURL, ArticleURL, msgFromNeon, PassHash, FirstShout, keychain)
        """
        LOG.info(f"Creating conversation {data}")
        new_cid = self._get_domain_cid(data[0], data[3])
        new_dom = data[0]
        self.server.emit("create conversation return", (new_cid, "title", None, new_dom), sid)

    def _change_domain(self, sid, *data):
        """
        Handle a request to change domains
        :param sid: SocketID associated with request
        :param data: ("this one", curr_cid, new_dom)
        """
        LOG.info(f"{sid} changing domains to {data[2]}")
        cid = self._get_domain_cid(data[2])
        dom = data[2]
        self.server.leave_room(sid, data[1])
        if self._socket_users[sid] in self._cid_nicks.get(cid, []):
            self._cid_nicks[cid].remove(self._socket_users[sid])
        self.server.enter_room(sid, cid)
        if not self._cid_nicks.get(cid):
            self._cid_nicks[cid] = list()
        self._cid_nicks[cid].append(self._socket_users[sid])

        if dom == "Private":
            title = f"!PRIVATE:{self._socket_users[sid]}"
        else:
            title = "Title"
        self.server.emit("new domain", (cid, None, {"dom": dom, "title": title}), sid)

    def _on_disconnect(self, sid, *data):
        """
        Handle a disconnected socket
        :param sid: SocketID disconnected
        :param data: ()
        """
        LOG.info(f"{sid} disconnected!")
        LOG.debug(data)
        try:
            self._socket_users.pop(sid)
        except Exception as e:
            LOG.error(e)

    def _search_shouts_by_phrase(self, sid, *data):
        """
        Handle a search request
        :param sid: SocketID associated with request
        :param data: (search_term, num_context, max_time)
        """
        LOG.debug(data)
        self.server.emit("search shouts by phrase return", ({}), sid)

    def _save_login(self, sid, *data):
        """
        Handle a Klat registration request
        :param sid: SocketID associated with request
        :param data: (username, domain, hash_pass, color, cid, kinstance, col1, 1col, 1?, 1?, speech_rate, stt_engine,
            tts_name, tts_gender, tts_language, tts_language_2, stt_language, time_format, units, date_format,
            city, state, country, uid, ?)
        """
        new_uname = data[0].lower()
        cid = data[4]
        old_nick = self._socket_users[sid]
        self._change_socket_nick(old_nick, new_uname, cid, sid)
        self.server.emit("save login return", (None, data[0], "Save login successful."), sid)

    def _get_log(self, sid, *data):
        """
        Handle a conversation log request
        :param sid: SocketID associated with request
        :param data: (myDomain, oldConversation, myConversation, myNick, myFollowsKey, myColumn,
            myMaxFollowedConversations, myContextMax, myContextTime, nano, lastShout, numShouts, function(err){})
        """
        dom = data[0]
        c_users = self._cid_nicks.get(dom)
        self.server.emit("chat log", ([], c_users), sid)

    def _set_server_event_listeners(self):
        self.server.on("get nicks for cid", self._get_nicks_for_cid)
        self.server.on("check login", self._check_login)
        self.server.on("logout", self._logout)
        self.server.on("nickname", self._nickname)
        self.server.on("user message", self._user_message)
        self.server.on("get conversation list 2", self._get_conversation_list)
        self.server.on("create conversation", self._create_conversation)
        self.server.on("change domain", self._change_domain)
        self.server.on("disconnect", self._on_disconnect)
        self.server.on("search shouts by phrase", self._search_shouts_by_phrase)
        self.server.on("save login", self._save_login)
        self.server.on("get log", self._get_log)


if __name__ == "__main__":
    server = MachKlatServer()
    server.t.join()
