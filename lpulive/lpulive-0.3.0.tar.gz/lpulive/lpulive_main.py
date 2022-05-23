'''
Author     : knight_byte ( Abunachar )
File       : lpulive_main.py
'''

# --------- Imports --------
from lpulive.lpulive_urls import (EDIT_USER_DETAIL, GET_CAHAT_MEMBERS_URL, GET_CONVRSATION_URL, GET_MESSAGES_THREADS_URL,
                                  GET_MESSAGES_URL, GET_WORKSPACE_DETAIL_URL,
                                  LOGIN_URL, LOGIN_VIA_TOKEN_URL, SEARCH_URL,
                                  SWITCH_WORKSPACE_URL)
import requests
import os
import pickle
import json


# -------- Main User class ------
class User:

    def __init__(self, registration_no, password) -> None:
        self.__REGNO = str(registration_no)
        self.__PASSWORD = str(password)
        self.__DATA_PATH = f"data_{self.__REGNO}.pkl"
        self.__LOGIN_SUCCESS = False
        self.__DATA_FILE = {}
        self.__HEADERS = {
            "user-agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0",
            "app_version": "1.0.0",
            "device_type": "WEB"}
        self.__DEVICE_DETAILS = json.dumps(
            {"browser-agent": str(self.__HEADERS['user-agent'])})
        self.__check_stored_data(self.__DATA_PATH)
        self.__WORKSPACE_ID = self.__DATA_FILE["workspace_id"] if self.__LOGIN_SUCCESS else None
        self.__USER_SESSION = self.__DATA_FILE["user_session"] if self.__LOGIN_SUCCESS else None
        self.__EN_USER_ID = self.__DATA_FILE["en_user_id"] if self.__LOGIN_SUCCESS else None
        self.__ACCESS_TOKEN = self.__DATA_FILE["access_token"] if self.__LOGIN_SUCCESS else None
        self.__LPU_ACCESS_TOKEN = self.__DATA_FILE["lpu_access_token"] if self.__LOGIN_SUCCESS else None
        self.__FULL_NAME = self.__DATA_FILE["full_name"] if self.__LOGIN_SUCCESS else None
        self.__FUGU_USER_ID = self.__DATA_FILE["fugu_user_id"] if self.__LOGIN_SUCCESS else None

    def __set_pickle_container(self, data_obj, data_path):
        with open(data_path, "wb") as pkl:
            pickle.dump(data_obj, pkl, pickle.HIGHEST_PROTOCOL)

    def __get_pickle_container(self, data_path):
        with open(data_path, "rb") as pkl:
            return pickle.load(pkl)

    def __check_stored_data(self, file_path) -> None:
        if not os.path.isfile(file_path):
            self.__login()

            if self.__LOGIN_SUCCESS:
                self.__DATA_FILE = self.__get_pickle_container(file_path)

        else:
            self.__DATA_FILE = self.__get_pickle_container(file_path)
            self.__LOGIN_SUCCESS = True

            if self.__REGNO != self.__DATA_FILE["regno"] or self.__DATA_FILE["password"] != self.__PASSWORD:
                self.__login()
                if self.__LOGIN_SUCCESS:
                    self.__DATA_FILE = self.__get_pickle_container(file_path)
                else:
                    self.__DATA_FILE = {}
                    self.__set_pickle_container({}, file_path)

    # login function

    def __login(self) -> None:
        self.__USER_SESSION = requests.session()
        json_data = {
            "password": self.__PASSWORD,
            "username": self.__REGNO,
            "domain": "lpu.in",
            "time_zone": 330
        }
        login_response = self.__USER_SESSION.post(
            url=LOGIN_URL, json=json_data, headers=self.__HEADERS)
        if login_response.status_code == 200:
            return_data = {}
            login_response_data = login_response.json()

            self.__WORKSPACE_ID = login_response_data["data"]["workspaces_info"][0]["workspace_id"]
            self.__ACCESS_TOKEN = login_response_data["data"]["user_info"]["access_token"]
            self.__LPU_ACCESS_TOKEN = login_response_data["data"]["user_info"]["lpu_access_token"]
            self.__EN_USER_ID = login_response_data["data"]["workspaces_info"][0]["en_user_id"]
            self.__FULL_NAME = login_response_data["data"]["workspaces_info"][0]["full_name"]
            self.__FUGU_USER_ID = login_response_data["data"]["workspaces_info"][0]["fugu_user_id"]
            return_data = {
                "workspace_id": self.__WORKSPACE_ID,
                "access_token": self.__ACCESS_TOKEN,
                "lpu_access_token": self.__LPU_ACCESS_TOKEN,
                "en_user_id": self.__EN_USER_ID,
                "user_session": self.__USER_SESSION,
                "password": self.__PASSWORD,
                "regno": self.__REGNO,
                "full_name": self.__FULL_NAME,
                "fugu_user_id": self.__FUGU_USER_ID
            }
            self.__LOGIN_SUCCESS = True
            self.__set_pickle_container(return_data, self.__DATA_PATH)
            self.__switch_workspace()
        else:
            self.__LOGIN_SUCCESS = False

    def __switch_workspace(self):
        sw_data = {
            "workspace_id": self.__WORKSPACE_ID,
            "access_token": self.__ACCESS_TOKEN,
            "device_details": json.dumps({"browser-agent": str(self.__HEADERS['user-agent'])}),
            "device_id": "random_text"
        }
        sw_response = self.__USER_SESSION.post(
            url=SWITCH_WORKSPACE_URL, json=sw_data, headers=self.__HEADERS)
        if sw_response.status_code == 200:
            self.__login_via_token()

    def __login_via_token(self):
        lvt_data = {
            "token": self.__ACCESS_TOKEN,
            "domain": "lpu.in",
            "lpu_access_token": self.__LPU_ACCESS_TOKEN,
            "time_zone": 330
        }
        lvt_headers = {"access_token": self.__ACCESS_TOKEN}
        lvt_headers.update(self.__HEADERS)
        self.__USER_SESSION.post(
            url=LOGIN_VIA_TOKEN_URL, json=lvt_data, headers=lvt_headers)

    def __get_workpace_details(self):
        gwsd_data = f"workspace=spaces&domain=lpu.in&device_id=random_text&device_details={self.__DEVICE_DETAILS}"
        self.__USER_SESSION.get(
            url=f"{GET_WORKSPACE_DETAIL_URL}?{gwsd_data}", headers=self.__HEADERS)

    def __get_conversation_filter(self, data) -> list:
        return_data = []
        for single in data:
            temp = {}
            temp["id"] = single["channel_id"]
            temp["chat_name"] = single["label"]
            temp["date_time"] = single["date_time"]
            temp["unread"] = single["unread_count"]
            return_data.append(temp)
        return return_data

    def __get_conversations_func(self) -> dict:
        if self.__LOGIN_SUCCESS:
            gc_data = f"en_user_id={self.__EN_USER_ID}&page_start=1&device_id=random_text&device_details={self.__DEVICE_DETAILS}"
            gc_responce = self.__USER_SESSION.get(
                url=f"{GET_CONVRSATION_URL}?{gc_data}", headers=self.__HEADERS)
            if gc_responce.status_code == 200:
                temp_data = gc_responce.json()["data"]
                total_chat = temp_data["count"]
                filter_chat_list = self.__get_conversation_filter(
                    temp_data["conversation_list"])
                final_data = {
                    "chats": filter_chat_list,
                    "total_chat": total_chat,
                }
                return final_data
            else:
                error_data = {
                    "message": "fail to fetch data"
                }
                return error_data
        else:
            return self.login_fail_message(type="dict")

    def __get_message_threads_func(self, chat_id, msg_id) -> list:
        if self.__LOGIN_SUCCESS:
            return_data = []
            gmt_data = f"muid={msg_id}&en_user_id={self.__EN_USER_ID}&channel_id={chat_id}"
            gmt_responce = self.__USER_SESSION.get(
                url=f"{GET_MESSAGES_THREADS_URL}?{gmt_data}", headers=self.__HEADERS)
            if gmt_responce.status_code == 200:
                temp_data = gmt_responce.json()["data"]["thread_message"]
                for single in temp_data:
                    temp = {
                        "from_user": single["full_name"].split(":")[0].strip(),
                        "regno": single["username"],
                        "message": single["message"],
                        "date": single["date_time"]
                    }
                    return_data.append(temp)
                return return_data
            else:
                return ["Fail to load thread, please check m_id"]
        else:
            return self.login_fail_message(type="list")

    def __get_messages_filter(self, data, chat_id, msg_thread=False) -> list:
        return_data = []
        for ind, single in enumerate(data[::-1]):
            temp = {
                "id": ind+1,
                "m_id": single["muid"],
                "message": single["message"],
                "date": single["date_time"],
                "from_user": single["full_name"].split(":")[0].strip(),
                "regno": single["username"],
                "attachment": False

            }
            if "url" in single:
                temp["attachment"] = {
                    "file_name": single["file_name"],
                    "url": single["url"],
                    "file_size": single["file_size"],
                    "type": single["document_type"]
                }
            if msg_thread:
                if single["thread_message_count"] > 0:
                    temp["thread"] = self.__get_message_threads_func(
                        chat_id, single["muid"])
                else:
                    temp["thread"] = "No thread"
            else:
                temp["thread"] = single["thread_message_count"]
            return_data.append(temp)
        return return_data

    def __get_messages_func(self, chat_id, msg_thread=False) -> dict:
        if self.__LOGIN_SUCCESS:
            gm_data = f"channel_id={chat_id}&en_user_id={self.__EN_USER_ID}&page_start=1&store_promise=true&device_id=random_text&device_details={self.__DEVICE_DETAILS}"
            gm_responce = self.__USER_SESSION.get(
                url=f"{GET_MESSAGES_URL}?{gm_data}", headers=self.__HEADERS)
            if gm_responce.status_code == 200:
                temp_data = gm_responce.json()["data"]
                filtered_messages = self.__get_messages_filter(
                    temp_data["messages"], chat_id, msg_thread)
                chat_name = temp_data["label"]
                user_name = temp_data["full_name"]
                total_messages = len(temp_data["messages"])
                final_data = {
                    "chat_id": chat_id,
                    "messages": filtered_messages,
                    "chat_name": chat_name,
                    "total_messages": total_messages,
                    "user_name": user_name,
                }
                with open("lpulive/test/data.json", "w") as f:
                    json.dump(final_data, f)
                return final_data
            else:
                error_data = {
                    "message": "fail to load messages, Please check chat_id"
                }
                return error_data
        else:
            return self.login_fail_message(type="dict")

    def __get_chat_members_filter(self, data):
        return_data = []
        for single in data:
            temp = {
                "name": single["full_name"].split(":")[0].strip(),
                "regno": single["email"],
                "profile_img": single["user_image"],
                "phone": single["contact_number"]
            }
            return_data.append(temp)
        return return_data

    def __get_chat_members_func(self, chat_id) -> dict:
        if self.__LOGIN_SUCCESS:
            def gcm_data_func(page):
                gcm_data2 = {"channel_id": chat_id,
                             "en_user_id": self.__EN_USER_ID,
                             "get_data_type": "MEMBERS",
                             "user_page_start": page}
                res = self.__USER_SESSION.get(
                    url=GET_CAHAT_MEMBERS_URL, json=gcm_data2, headers=self.__HEADERS)
                if res.status_code == 200:
                    return res.json()["data"]["chat_members"]
                else:
                    return None

            return_data = []
            for page in range(0, 5000, 51):
                x = gcm_data_func(page=page)
                if x == None:
                    return {"message": "Fail to fetch members, Please check chat_id"}
                elif len(x) < 1:
                    break
                else:
                    return_data += x
            final_data = {
                "chat_id": chat_id,
                "members": self.__get_chat_members_filter(return_data),
                "total_members": len(return_data)
            }
            return final_data
        else:
            return self.login_fail_message(type="dict")

    def __search_user_filter(self, data):
        return_data = []
        for ind, single in enumerate(data):
            temp = {
                "id": ind+1,
                "name": single["full_name"].split(":")[0].strip(),
                "regno": single["email"],
                "department": single["department"],
                "profile_img": single["user_image"]
            }
            return_data.append(temp)
        return return_data

    def __search_user_func(self, user) -> dict:
        if self.__LOGIN_SUCCESS:
            if len(user) < 3:
                return {"message": "Search Query must be atleast 2 character long"}
            su_data = {
                "en_user_id": self.__EN_USER_ID,
                "search_text": user,
                "user_role": "USER",
                "search_deactivated_member": "true"
            }
            su_response = self.__USER_SESSION.get(
                url=SEARCH_URL, json=su_data, headers=self.__HEADERS)
            if su_response.status_code == 200:
                data = su_response.json()["data"]["users"]
                users = self.__search_user_filter(data)
                return_data = {
                    "search_query": user,
                    "users": users,
                    "total_found": len(users)
                }
                return return_data

            else:
                return {"message": "fail to fetch, please try again later"}
        else:
            return self.login_fail_message(type="dict")

    def login_fail_message(self, type="str"):
        if type == "dict":
            return {"message": "fail to login, check user details"}
        elif type == "list":
            return ["fail to login, check user details"]
        else:
            return "fail to login, check user details"

    """# ------------------------ USER AVAILABLE METHODS ------------------------------ #"""

    # ----------GET CONVERSATION METHOD --------------
    '''
    - To get all the active chat
    - function takes no argument
    - function return a dictionary object
        > chats : list of all the chat active on users profile
            -> id : id of particular chat
            -> chat_name : name of the chat
            -> date_time : last acitve message on that chat
            -> unread : total unread messages on that chat
        > total_chat : total group/private chat active on users profiles
    '''

    def get_conversations(self) -> dict:
        return self.__get_conversations_func()

    # ---------GET MESSAGES METHOD ------------
    '''
    - To get all the messages of selected chat
    - functions takes to argument chat_id, msg_thread
        > chat_id : to select a particular chat to get all messages [ required argument ]
        > msg_thread : to turn on thread, this will also include the threads of messages ( if appicable ) [ default value is False ]
    - function return a dictionary object
        > chat_id : id of the chat
        > messages : list of all the messages in that chat
            -> id : id number ( smaller the id newer the message )
            -> m_id : message id
            -> message : text message
            -> from_user : message sender name
            -> regno : message sender registration number
            -> attachment : any attachment in that message ( if applicable )
            -> thread_message : get all the thread of a particular message ( if msg_thread is True )
        > chat_name : name of the chat
        > total_messages : total messages in that chat
        > user_name : name of current user
    '''

    def get_messages(self, chat_id, msg_thread=False) -> dict:
        return self.__get_messages_func(chat_id=chat_id, msg_thread=msg_thread)

    # -------------- GET MESSAGE THREAD METHOD --------------
    '''
    - To get the thread of particular message
    - function takes to parameter chat_id, msg_id
        > chat_id : chat_id of the chat
        > msg_id : message id for which thread is to be extracted
    - Function returns a dictionary object of thread message of that message
        > chat_id : chat_id of the chat
        > msg_id : message id of the chat
        > messages : messages of all the thread
        > total_thread : count of total messages in thread
    '''

    def get_message_threads(self, chat_id, msg_id) -> dict:
        messages = self.__get_message_threads_func(
            chat_id=chat_id, msg_id=msg_id)
        temp_data = {
            "chat_id": chat_id,
            "msg_id": msg_id,
            "messages": messages,
            "total_thread": len(messages)
        }
        return temp_data

    # ------------ LOGOUT METHOD ---------------
    '''
    - Logout the user from local session
    - Clears up all the local cache
    - function takes no argument
    - function return a string object
    '''

    def logout(self) -> str:
        try:
            os.remove(self.__DATA_PATH)
            return "Successfully logged out and cleared local cache"
        except Exception:
            return "Fail to logout and clear cache"

    # ------------GET CHAT MEMBERS METHOD -----------
    '''
    - To get all the members list in a particular channel
    - function takes one argument chat_id
        > chat_id : chat_id of the chat
    - function returns a dictionary object
        > chat_id : chat_id of the chat
        > members : list of members
            -> name : name of the member
            -> regno : registration number
            -> profile_img : profile image of the member
            -> phone : phone number ( if available )
        > total_members : count fof total members
    '''

    def get_chat_members(self, chat_id) -> dict:
        return self.__get_chat_members_func(chat_id=chat_id)

    # ------------ SEARCH USER METHOD ----------
    '''
    - To search user
    - function takes one argument query
        > query : search query
    - function returns a dictionary object
        > search_query : search query
        > users : list of users found
            -> id : id
            -> name : name of the user
            -> regno : registration number of the user
            -> department : department/batch of the user
            -> profile_img : profile image of the user
        > total_found : total user matched the query
    '''

    def search_users(self, query):
        return self.__search_user_func(user=query)
