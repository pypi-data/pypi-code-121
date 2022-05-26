#
# YTRequests
# ©2022 tsubasa652 All Rights Reserved.
# MIT Licensed
#

import requests

class YTRequestsError(Exception):
    """
    If the request is not successful
    """

    pass

class YTArgumentError(Exception):
    """
    If the argument is not valid
    """
    pass

class YTRequests:
    """
    YouTube Data V3 API

    Raises:
        YTArgumentError: If the argument is not valid
        YTRequestsError: If the request is not successful
    """

    __base_url = 'https://www.googleapis.com/youtube/v3'
    __unofficial_api_key = 'AIzaSyAa8yy0GdcGPHdtD083HiGGx_S0vMPScDM'
    __base_headers = {
        "content-type": "application/json"
    }

    def __init__(self, api_key = None, unofficial = False, proxies=None):
        """
        initialize YTRequests

        Args:
            api_key (str, optional): YouTube Data API V3 API Key. Defaults to None.
            unofficial (bool, optional): use UnOfficial mode. Defaults to False.

        Raises:
            YTArgumentError: If the argument is not valid
        """
        self.proxies = proxies
        if unofficial:
            self.__base_headers["x-origin"] = "https://explorer.apis.google.com"
            self.__api_key = self.__unofficial_api_key
        elif api_key:
            self.__api_key = api_key
        else:
            raise YTArgumentError("No API key provided")
    
    # def get_video_info(self, videoId):
    #     params = {

    #     }

    def get_comments(self, videoId):
        """
        Get comments of a video

        Args:
            videoId (str): videoId

        Raises:
            YTRequestsError: If the request is not successful

        Returns:
            list: comments
        """
        params = {
            "part": "id,snippet,replies",
            "maxResults": 50,
            "videoId": videoId,
            "key": self.__api_key
        }

        nextToken = None
        items = []

        while True:
            if nextToken:
                params["pageToken"] = nextToken
            r = requests.get(f"{self.__base_url}/commentThreads", params=params, headers=self.__base_headers, timeout=10, proxies=self.proxies)
            if r.status_code != 200:
                if len(items) > 0:
                    return items

                raise YTRequestsError(r.status_code, r.text)

            data = r.json()
            items.extend(data["items"])
            nextToken = data.get("nextPageToken")
            if not nextToken:
                break

        return items

    def search_videos(self, word, _type=["video","channel","playlist"], max_results=None):
        """
        Search videos

        Args:
            word (str): search word
            _type (list or str, optional): search type. Defaults to ["video","channel","playlist"].
            max_results (int, optional): The maxResults parameter specifies the maximum number of items that should be returned in the result set. Defaults to None.

        Raises:
            YTRequestsError: If the request is not successful

        Returns:
            list: videos
        """
        if type(_type) == list:
            _type = ",".join(_type)

        params = {
            "part": "id,snippet",
            "maxResults": 50,
            "q": word,
            "type": _type,
            "key": self.__api_key
        }

        nextToken = None
        items = []

        while True:
            if nextToken:
                params["pageToken"] = nextToken
            r = requests.get(f"{self.__base_url}/search", params=params, headers=self.__base_headers, timeout=10, proxies=self.proxies)
            if r.status_code != 200:
                if len(items) > 0:
                    return items

                raise YTRequestsError(r.status_code, r.text)

            data = r.json()
            items.extend(data["items"])
            if max_results and len(items) >= max_results:
                return items[0:max_results]
            nextToken = data.get("nextPageToken")
            if not nextToken:
                break

        return items

    def get_video_info(self, _id, parts=None):
        """
        Get video info

        Args:
            _id (str or list): videoId or list of videoId
            parts (str or list, optional): _description_. Defaults to id,snippet,contentDetails and more.

        Raises:
            YTArgumentError: If the argument is not valid
            YTRequestsError: If the request is not successful

        Returns:
            list: video info
        """
        if not parts:
            parts = [
                "id",
                "snippet",
                "contentDetails",
                # "fileDetails",
                "liveStreamingDetails",
                "player",
                # "processingDetails",
                "recordingDetails",
                "statistics",
                "status",
                # "suggestions",
                "topicDetails"
            ]

        if type(parts) == list:
            parts = ",".join(parts)
        elif type(parts) != str:
            raise YTArgumentError("parts must be a list or a string")
        if type(_id) == list:
            _id = ",".join(_id)
        elif type(_id) != str:
            raise YTArgumentError("_id must be a list or a string")
        params = {
            "part": parts,
            "id": _id,
            "key": self.__api_key
        }
        r = requests.get(f"{self.__base_url}/videos", params=params, headers=self.__base_headers, timeout=10, proxies=self.proxies)
        if r.status_code != 200:
            raise YTRequestsError(r.status_code, r.text)

        return r.json()["items"]