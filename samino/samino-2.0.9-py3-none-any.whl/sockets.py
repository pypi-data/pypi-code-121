# those sockets are based on: Amino-Sockets / Amino.py
# Modified by SirLez, zett.0
import requests
import websocket
import threading
import time as timer
import ujson as json
from typing import BinaryIO
from sys import _getframe as getframe

from .lib import util, headers
from .lib.objects import Event, Payload
from .lib.exception import CheckExceptions as exception


class Callbacks:
    def __init__(self):
        self.handlers = {}

        self.methods = {
            10: self._resolve_payload,
            304: self._resolve_chat_action_start,
            306: self._resolve_chat_action_end,
            1000: self._resolve_chat_message
        }

        self.chat_methods = {
            "0:0": self.on_text_message,
            "0:100": self.on_image_message,
            "0:103": self.on_youtube_message,
            "1:0": self.on_strike_message,
            "2:110": self.on_voice_message,
            "3:113": self.on_sticker_message,
            "50:0": self.TYPE_USER_SHARE_EXURL,
            "51:0": self.TYPE_USER_SHARE_USER,
            "52:0": self.on_voice_chat_not_answered,
            "53:0": self.on_voice_chat_not_cancelled,
            "54:0": self.on_voice_chat_not_declined,
            "55:0": self.on_video_chat_not_answered,
            "56:0": self.on_video_chat_not_cancelled,
            "57:0": self.on_video_chat_not_declined,
            "58:0": self.on_avatar_chat_not_answered,
            "59:0": self.on_avatar_chat_not_cancelled,
            "60:0": self.on_avatar_chat_not_declined,
            "100:0": self.on_delete_message,
            "101:0": self.on_group_member_join,
            "102:0": self.on_group_member_leave,
            "103:0": self.on_chat_invite,
            "104:0": self.on_chat_background_changed,
            "105:0": self.on_chat_title_changed,
            "106:0": self.on_chat_icon_changed,
            "107:0": self.on_voice_chat_start,
            "108:0": self.on_video_chat_start,
            "109:0": self.on_avatar_chat_start,
            "110:0": self.on_voice_chat_end,
            "111:0": self.on_video_chat_end,
            "112:0": self.on_avatar_chat_end,
            "113:0": self.on_chat_content_changed,
            "114:0": self.on_screen_room_start,
            "115:0": self.on_screen_room_end,
            "116:0": self.on_chat_host_transfered,
            "117:0": self.on_text_message_force_removed,
            "118:0": self.on_chat_removed_message,
            "119:0": self.on_text_message_removed_by_admin,
            "120:0": self.on_chat_tip,
            "121:0": self.on_chat_pin_announcement,
            "122:0": self.on_voice_chat_permission_open_to_everyone,
            "123:0": self.on_voice_chat_permission_invited_and_requested,
            "124:0": self.on_voice_chat_permission_invite_only,
            "125:0": self.on_chat_view_only_enabled,
            "126:0": self.on_chat_view_only_disabled,
            "127:0": self.on_chat_unpin_announcement,
            "128:0": self.on_chat_tipping_enabled,
            "129:0": self.on_chat_tipping_disabled,
            "65281:0": self.on_timestamp_message,
            "65282:0": self.on_welcome_message,
            "65283:0": self.on_invite_message
        }

        self.notif_methods = {
            "53": self.on_member_set_you_host,
            "67": self.on_member_set_you_cohost,
            "68": self.on_member_remove_you_cohost
        }

        self.chat_actions_start = {
            "Typing": self.on_user_typing_start,
        }

        self.chat_actions_end = {
            "Typing": self.on_user_typing_end,
        }

    def _resolve_payload(self, data):
        key = f"{data['o']['payload']['notifType']}"
        return self.notif_methods.get(key, self.default)(data)

    def _resolve_chat_message(self, data):
        key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
        return self.chat_methods.get(key, self.default)(data)

    def _resolve_chat_action_start(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_start.get(key, self.default)(data)

    def _resolve_chat_action_end(self, data):
        key = data['o'].get('actions', 0)
        return self.chat_actions_end.get(key, self.default)(data)

    def resolve(self, data):
        data = json.loads(data)
        return self.methods.get(data["t"], self.default)(data)

    def call(self, type, data):
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(data)

    def event(self, type):
        def registerHandler(handler):
            if type in self.handlers:
                self.handlers[type].append(handler)
            else:
                self.handlers[type] = [handler]
            return handler

        return registerHandler

    def on_member_set_you_host(self, data): self.call(getframe(0).f_code.co_name, Payload(data["o"]).Payload)
    def on_member_remove_you_cohost(self, data): self.call(getframe(0).f_code.co_name, Payload(data["o"]).Payload)
    def on_member_set_you_cohost(self, data): self.call(getframe(0).f_code.co_name, Payload(data["o"]).Payload)

    def on_text_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_image_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_youtube_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_strike_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_sticker_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def TYPE_USER_SHARE_EXURL(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def TYPE_USER_SHARE_USER(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_video_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_video_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_video_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_avatar_chat_not_answered(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_avatar_chat_not_cancelled(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_avatar_chat_not_declined(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_delete_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_group_member_join(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_group_member_leave(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_invite(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_background_changed(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_title_changed(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_icon_changed(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_start(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_video_chat_start(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_avatar_chat_start(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_end(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_video_chat_end(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_avatar_chat_end(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_content_changed(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_screen_room_start(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_screen_room_end(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_host_transfered(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_text_message_force_removed(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_removed_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_text_message_removed_by_admin(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_tip(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_pin_announcement(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_permission_open_to_everyone(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_permission_invited_and_requested(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_voice_chat_permission_invite_only(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_view_only_enabled(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_view_only_disabled(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_unpin_announcement(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_tipping_enabled(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_chat_tipping_disabled(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_timestamp_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_welcome_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_invite_message(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)

    def on_user_typing_start(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)
    def on_user_typing_end(self, data): self.call(getframe(0).f_code.co_name, Event(data["o"]).Event)

    def default(self, data): self.call(getframe(0).f_code.co_name, data)


class SetAction:
    def __init__(self, wss, data):
        self.action = data
        self.wss = wss

    def start(self):
        """
        Start the Action
        """
        self.wss.send(self.action)

    def stop(self):
        """
        Get back to the last board
        """
        act = self.action
        act["t"] = 303
        self.wss.send(self.action)


class Actions:
    def __init__(self, socket, comId, chatId):
        self.socket = socket
        self.chatId = chatId
        self.comId = comId

    def default(self):
        """
        Default Browsing
        """
        SetAction(self.socket, {
            "o": {"actions": ["Browsing"], "target": f"ndc://x{self.comId}/", "ndcId": int(self.comId),
                  "params": {"duration": 27605}, "id": "363483"}, "t": 306}).start()

    def Browsing(self, blogId: str = None, blogType: int = 0):
        """
        Send Browsing Action

        **Paramaters**
            - **blogId**: 2 For Public 1 & 0 For Private (str)
            - **blogType**: Type Of the Blog *poll & blog & wiki* (int)

        **Return**
            - **SetAction**:  (Class)
        """
        if blogId and blogType:
            target = f"ndc://x{self.comId}/blog/"
        else:
            target = f"ndc://x{self.comId}/featured"

        data = {
            "o": {
                "actions": ["Browsing"],
                "target": target,
                "ndcId": int(self.comId),
                "params": {"blogType": blogType},
                "id": "363483"
            },
            "t": 306
        }
        self.default()
        return SetAction(self.socket, data)

    def Chatting(self, threadType: int = 2):
        """
        Send Chatting Action

        **Paramaters**
            - **threadType**: 2 For Public 1 & 0 For Private (int)

        **Return**
            - **SetAction**:  (Class)
        """
        data = {
            "o": {
                "actions": ["Chatting"],
                "target": f"ndc://x{self.comId}/chat-thread/{self.chatId}",
                "ndcId": int(self.comId),
                "params": {
                    "duration": 12800,
                    "membershipStatus": 1,
                    "threadType": threadType
                },
                "id": "1715976"
            },
            "t": 306
        }
        self.default()
        return SetAction(self.socket, data)

    def PublicChats(self):
        """
        Send PublicChats Action

        **Return**
            - **SetAction**:  (Class)
        """
        data = {
            "o": {
                "actions": ["Browsing"],
                "target": f"ndc://x{self.comId}/public-chats",
                "ndcId": int(self.comId),
                "params": {"duration": 859},
                "id": "363483"
            },
            "t": 306
        }
        self.default()
        return SetAction(self.socket, data)

    def LeaderBoards(self):
        """
        Send LeaderBoard Action

        **Return**
            - **SetAction**:  (Class)
        """
        data = {
            "o": {
                "actions": ["Browsing"],
                "target": f"ndc://x{self.comId}/leaderboards",
                "ndcId": int(self.comId),
                "params": {"duration": 859},
                "id": "363483"
            },
            "t": 306
        }
        self.default()
        return SetAction(self.socket, data)

    def Custom(self, actions: [str, list], target: str, params: dict):
        """
        Send Custom Action

        **Parameters**
            - **actions**: List of action Types (list[str])
            - **target**: Example | ndc://x000000/leaderboards (str)
            - **params**: Set the blogType and more with params (dict)

        **Return**
            - **SetAction**:  (Class)
        """
        data = {
            "o": {
                "actions": actions,
                "target": target,
                "ndcId": int(self.comId),
                "params": params,
                "id": "363483"
            },
            "t": 306
        }
        self.default()
        return SetAction(self.socket, data)


class WssClient:
    def __init__(self, wss):
        self.wss = wss


    def joinVoiceChat(self, comId: str, chatId: str, joinType: int = 1):

        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "joinRole": joinType,
                "id": "37549515"
            },
            "t": 112
        }
        timer.sleep(2.2)
        self.wss.send(data)

    def joinVideoChat(self, comId: str, chatId: str, joinType: int = 1):
        """
        Join The Video Chat

        **Parameters**
            - **comId**: ID of the Community (str)
            - **chatId**: ID of the Chat (str)
            - **joinType**: Join type to Join Video as.. (int)
        """
        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "joinRole": joinType,
                "channelType": 5,
                "id": "2154531"
            },
            "t": 108
        }
        timer.sleep(2.2)
        self.wss.send(data)

    def startVoiceChat(self, comId, chatId: str, joinType: int = 1):
        """
        Start The Voice Chat

        **Parameters**
            - **comId**: ID of the Community (str)
            - **chatId**: ID of the Chat (str)
            - **joinType**: Join type to Start voice as.. (int)
        """
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": joinType,
                "id": "2154531"
            },
            "t": 112
        }
        timer.sleep(2.2)
        self.wss.send(data)
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "channelType": 1,
                "id": "2154531"
            },
            "t": 108
        }
        timer.sleep(2.2)
        self.wss.send(data)

    def endVoiceChat(self, comId: str, chatId: str, leaveType: int = 2):
        """
        End The Voice Chat

        **Parameters**
            - **comId**: ID of the Community (str)
            - **chatId**: ID of the Chat (str)
            - **leaveType**: Leave type to end voice as.. (int)
        """
        data = {
            "o": {
                "ndcId": comId,
                "threadId": chatId,
                "joinRole": leaveType,
                "id": "2154531"
            },
            "t": 112
        }
        timer.sleep(2.2)
        self.wss.send(data)

    def joinVideoChatAsSpectator(self, comId: str, chatId: str):
        """
        Join Video Chat As Spectator

        **Parameters**
            - **comId**: ID of the Community (str)
            - **chatId**: ID of the Chat (str)
        """
        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "joinRole": 2,
                "id": "72446"
            },
            "t": 112
        }
        timer.sleep(2.2)
        self.wss.send(data)

    def threadJoin(self, comId: str, chatId: str):
        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "joinRole": 1,
                "id": "10335106"
            },
            "t": 112
        }
        self.wss.send(data)

    def channelJoin(self, comId: str, chatId: str):
        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "channelType": 5,
                "id": "10335436"
            },
            "t": 108
        }
        self.wss.send(data)

    def videoPlayer(self, comId: str, chatId: str, path: str, title: str, background: str, duration: int):
        self.actions(comId, chatId).Chatting().start()
        self.threadJoin(comId, chatId)
        self.channelJoin(comId, chatId)
        data = {
            "o": {
                "ndcId": int(comId),
                "threadId": chatId,
                "playlist": {
                    "currentItemIndex": 0,
                    "currentItemStatus": 1,
                    "items": [{
                        "author": None,
                        "duration": duration,
                        "isDone": False,
                        "mediaList": [[100, background, None]],
                        "title": title,
                        "type": 1,
                        "url": f"file://{path}"
                    }]
                },
                "id": "3423239"
            },
            "t": 120
        }
        self.wss.send(data)
        timer.sleep(2)
        data["o"]["playlist"]["currentItemStatus"] = 2
        data["o"]["playlist"]["items"][0]["isDone"] = True
        self.wss.send(data)

    def playVideo(self, comId: str, chatId: str, path: str, title: str, background: BinaryIO, duration: int):
        """
        Play Custom Video

        **Parameters**
            - **comId** : ID of the Community (str)
            - **chatId** : ID of the Chat (str)
            - **path** : Video Path | /storage/emulated/0/Download/video.mp4 (str)
            - **title** : Video Title (str)
            - **background** : Background of the video (BinaryIO)
            - **duration** : length of the mp4/mp3 (int)
        """
        threading.Thread(target=self.videoPlayer, args=(comId, chatId, path, title, self.wss.uploadMedia(background, "image"), duration)).start()

    def getActionUsers(self, comId: str, path: str):
        """
        Get Action Users

        **Parameters**
            - **comId**: ID of the Community (str)
            - **path**: Example: "users-chatting" (str)
        """
        data = {
            "o": {
                "ndcId": int(comId),
                "topic": f"ndtopic:x{comId}:{path}",
                "id": "4538416"
            },
            "t": 300
        }
        timer.sleep(2)
        self.wss.send(data)
        data["t"] += 2
        self.wss.send(data)
        timer.sleep(0.50)
        return self.wss.receive()

    def actions(self, comId: str, chatId: str):
        threading.Thread(target=self.wss.sendWebActive, args=(comId, )).start()
        return Actions(self.wss, comId, chatId)


class Wss(Callbacks, WssClient):
    def __init__(self, client, trace: bool = False):

        self.client = client
        self.isOpened = False
        Callbacks.__init__(self)
        WssClient.__init__(self, self)
        self.narvi = "https://service.narvii.com/api/v1/"
        self.socket_url = "wss://ws1.narvii.com"
        self.lastMessage = {}
        websocket.enableTrace(trace)

    def onOpen(self, ws=None):
        self.isOpened = True

    def onClose(self, ws=None):
        self.isOpened = False

    def send(self, data):
        self.socket.send(json.dumps(data))

    def receive(self):
        return self.lastMessage

    def on_message(self, data):
        self.lastMessage = json.loads(data)
        self.resolve(data)

    def launch(self):
        final = f"{self.client.deviceId}|{int(timer.time() * 1000)}"
        self.headers = {
            "NDCDEVICEID": self.client.deviceId,
            "NDCAUTH": self.client.sid,
            "NDC-MSG-SIG": util.s(data=final)}
        self.socket = websocket.WebSocketApp(f"{self.socket_url}/?signbody={final.replace('|', '%7C')}",
                                             on_message=self.on_message,
                                             on_close=self.onClose,
                                             on_open=self.onOpen,
                                             header=self.headers)
        threading.Thread(target=self.socket.run_forever, kwargs={"ping_interval": 60}).start()

    def close(self):
        self.socket.close()

    def status(self):
        return self.isOpened

    def uploadMedia(self, file: BinaryIO, fileType: str):
        if fileType == "audio":typee = "audio/aac"
        elif fileType == "image":typee = "image/jpg"
        else:raise TypeError("[i] Report this error in Discord Server as [15:0]")

        data = file.read()
        headers = self.headers
        headers["content-type"] = typee
        headers["content-length"] = str(len(data))

        response = requests.post(f"{self.narvi}/g/s/media/upload", data=data, headers=headers)
        if response.json()["api:statuscode"] != 0:return exception(response.json())
        else:return response.json()["mediaValue"]

    def sendWebActive(self, comId: str):
        data = {"ndcId": comId}
        response = requests.post("https://aminoapps.com/api/community/stats/web-user-active-time", json=data, headers=headers.Headers().web_headers)
        if response.json()["code"] != 200:return exception(response.json())
        else:return response
