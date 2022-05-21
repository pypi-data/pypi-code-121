import aiohttp
import re
import json
import pathlib

ROOT = "https://www.wykop.pl"

def _json_loads(body, **kwargs):
    PREFIX = "for(;;);"

    return json.loads(body[len(PREFIX):], **kwargs)

async def _check_json(response):
    if response.status == 200:
        response_json = await response.json(loads=_json_loads)

        if "error" not in response_json:
            return response_json
        else:
            error_message = response_json["error"]["message"]

            raise Exception(f"api error: {error_message}")
    else:
        raise Exception(f"unexpected response status: {response.status}")

async def _post(client, url, data):
    async with client.post(url, data=data) as response:
        return await _check_json(response)

class Session(object):
    def __init__(self, login_cookie, *, client = None, wykop_hash = None, user_agent = None, jsessionidn = None, **kwargs):
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"
        JSESSIONIDN = "s-24"

        kwargs = {}
        kwargs["headers"] = { "User-Agent": user_agent or USER_AGENT }
        kwargs["cookies"] = {
            "JSESSIONIDN": jsessionidn or JSESSIONIDN,
            "login": login_cookie
        }

        self.__client = aiohttp.ClientSession(**kwargs)
        self.__wykop_hash = wykop_hash
    
    def requires_hash(fn):
        async def wrapper(self, *args, **kwargs):
            if self.__wykop_hash is None:
                async with self.__client.get(ROOT) as response:
                    body = await response.text()

                    match = re.search("hash\\s+:\\s+\\\"(?P<hash>[0-f]{32}-[0-9]{10})\\\"", body)

                    if match is not None:
                        wykop_hash = match.group("hash")
                        self.__wykop_hash = wykop_hash
                    else:
                        raise Exception("couldn't scrap hash value")

            return await fn(self, *args, **kwargs)

        return wrapper

    @requires_hash
    async def attach_url(self, url):
        form = { "url": url }

        response_json = await _post(self.__client, f"{ROOT}/ajax2/embed/url/hash/{self.__wykop_hash}/", data=form)
        return response_json["operations"][0]["data"]["hash"]

    @requires_hash
    async def attach_file(self, file, *, rename = None):
        CONTENT_TYPE = "application/octet-stream"

        if not isinstance(file, pathlib.Path):
            file = pathlib.Path(file)

        with file.open("rb") as file_handle:
            form = aiohttp.FormData()
            form.add_field("file_element", "file")
            form.add_field("file", file_handle, filename=rename or file.name, content_type=CONTENT_TYPE)

            response_json = await _post(self.__client, f"{ROOT}/ajax2/embed/upload/hash/{self.__wykop_hash}/", data=form)
            return response_json["operations"][0]["data"]["hash"]

    @requires_hash
    def post(self, body = None, attachment_id = None):
        form = {
            "body": body or "",
            "parent_id": "",
            "attachment": attachment_id or "",
        }

        return _post(self.__client, f"{ROOT}/ajax2/wpis/dodaj/hash/{self.__wykop_hash}/", data=form)

    @requires_hash
    def comment(self, post_id, body = None, attachment_id = None):
        form = {
            "body": body or "",
            "parent_id": "",
            "attachment": attachment_id or "",
        }
        
        return _post(self.__client, f"{ROOT}/ajax2/wpis/CommentAdd/{post_id}/hash/{self.__wykop_hash}/", data=form)

    @requires_hash
    def observe(self, username):
        return self.__client.get(f"{ROOT}/ajax2/ludzie/observe/{username}/{self.__wykop_hash}//hash/{self.__wykop_hash}")

    @requires_hash
    def unobserve(self, username):
        return self.__client.get(f"{ROOT}/ajax2/ludzie/unobserve/{username}/{self.__wykop_hash}//hash/{self.__wykop_hash}")

    @requires_hash
    def edit_post(self, post_id, body = None, attachment_id = None):
        form = {
            "body": body or "",
            "parent_id": "",
            "attachment": attachment_id or "",
        }

        return _post(self.__client, f"{ROOT}/ajax2/wpis/edytuj/{post_id}//hash/{self.__wykop_hash}/", data=form)

    @requires_hash
    def edit_comment(self, comment_id, body = None, attachment_id = None):
        form = {
            "body": body or "",
            "parent_id": "",
            "attachment": attachment_id or "",
        }

        return _post(self.__client, f"{ROOT}/ajax2/wpis/commentedit/{comment_id}//hash/{self.__wykop_hash}/", data=form)

    @requires_hash
    def delete_post(self, post_id):
        return self.__client.get(f"{ROOT}/ajax2/wpis/usun/{post_id}/hash/{self.__wykop_hash}/")

    @requires_hash
    def delete_comment(self, comment_id):
        return self.__client.get(f"{ROOT}/ajax2/wpis/commentdelete/{comment_id}/hash/{self.__wykop_hash}/")

    async def close(self):
        if self.__client is not None:
            await self.__client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.__client is not None:
            await self.__client.close()
