from datetime import datetime
import functools
import json
from multiprocessing import Process
import re
import threading
import requests
from werkzeug.wrappers import Request, Response

from .client_ip import ClientIp
from .models.user import User
from .models.product import Product
from .tasks.background_tasks import BackgroundTasks

base_url = "https://api.archetype.dev"
test_url = "https://test.archetype.dev"

headers = {}


class Archetype:
    def __init__(self, settings):
        self.app_id = settings["app_id"]
        self.secret_key = settings["secret_key"]
        self.headers = {
            "X-Archetype-SecretKey": self.secret_key,
            "X-Archetype-AppID": self.app_id,
        }
        if "sk_test" in self.secret_key:
            self.env = "test"
        else:
            self.env = "prod"

    def authorize(self, *args, **kwargs):
        request = kwargs.get("request", None)
        start_time = datetime.utcnow().timestamp()

        def wrapper_key_required(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if request and request.headers.get("apikey"):
                    data = {
                        "path": request.path,
                        "method": request.method,
                        "url_apikey": "",
                        "body_apikey": "",
                        "header_apikey": request.headers.get("apikey"),
                    }
                    x = Utils.post(
                        env=self.env,
                        path="/sdk/v2/authorize",
                        data=data,
                        headers=self.headers,
                    )
                    if x.status_code < 400:
                        res = func(*args, **kwargs)

                    elif x.status_code == 400:
                        res = Response(
                            json.dumps({"error": "Rate limit / Quota Exceeded"}),
                            mimetype="text/plain",
                            status=401,
                        )
                    elif x.status_code == 401:
                        res = Response(
                            json.dumps(
                                {"error": "User doesn't have access to this endpoint"}
                            ),
                            mimetype="text/plain",
                            status=401,
                        )

                    elif x.status_code == 403:
                        res = Response(
                            json.dumps({"error": "Invalid/Incorrect API key"}),
                            mimetype="text/plain",
                            status=403,
                        )
                    else:
                        res = Response(
                            json.dumps({"error": "Authorization failed"}),
                            mimetype="text/plain",
                            status=x.status_code,
                        )
                else:
                    res = Response(
                        json.dumps({"error": "API Key not supplied. Add an 'apikey' field to the headers with your provided API key"}),
                        mimetype="text/plain",
                        status=403,
                    )
                _send_log_details(
                    app_id=self.app_id,
                    status_code=res.status_code,
                    request=request,
                    start_time=start_time,
                    request_body=get_request_body(request=request),
                )
                return res

            wrapper.__name__ = func.__name__
            return wrapper

        return wrapper_key_required

    def log(uid=None,apikey=None,billable_metric=None,amount:float=0):
        pass

    def user(self, uid=None, email=None, name=None, attrs={}):
        if not uid:
            return None
        if not Utils.is_url_readable(uid):
            print("UID is invalid or unparseable.")
            return None

        user = self.get_user_details(uid=uid)
        if not user:
            user = self._register(uid=uid, email=email, name=name)
        return user

    def _register(self, uid, email=None, name=None):
        if uid is None or not Utils.is_url_readable(uid):
            print("UID is invalid or unparseable.")
            return None
        data = {
            "custom_uid": uid,
            "name": str(name) if name is not None else None,
            "email": str(email) if email is not None else None,
        }
        response = Utils.post(
            env=self.env, path="/sdk/v1/create-user", data=data, headers=self.headers
        )
        if response.status_code == 200:
            return User(source=response.json())
        else:
            return None

    def get_user_details(self, uid):
        if uid is None or not Utils.is_url_readable(uid):
            print("UID is invalid or unparseable.")

        response = Utils.get(
            env=self.env, path=f"/sdk/v2/user/{uid}", args={}, headers=self.headers
        )
        if response.status_code == 404:
            return None
        return User(source=response.json())

    def set_user_details(self, uid, email=None, name=None, company=None, attrs=None):
        data = {"custom_uid": uid}
        if email:
            data["email"] = email
        if name:
            data["name"] = name
        if company:
            data["company"] = company
        if attrs:
            data["attrs"] = attrs

        response = Utils.put(path="/sdk/v2/user", data=data, headers=self.headers)
        if response.status_code == 404:
            print(f"User {uid} doesn't exist")
            return None
        return User(source=response.json())

    def get_all_products(self, as_json=False):
        response = Utils.post(env=self.env, path="/sdk/v1/tiers", headers=self.headers)
        if response.status_code != 200:
            raise Exception

        all_tiers_json = response.json()
        if as_json:
            return all_tiers_json
        all_tiers = [Product(source=source) for source in all_tiers_json]
        return all_tiers

    # cancel a subscription for the user
    def cancel_subscription(self, uid, cancel_immediately=False):
        data = {
            "custom_uid": uid,
            "cancel_immediately": cancel_immediately
        }
        response = Utils.post(
            env=self.env,
            path="/sdk/v1/cancel-subscription",
            data=data,
            headers=self.headers,
        )
        if response.status_code == 200:
            return {"success": "User subscription successfully canceled"}
        if response.status_code == 400:
            return {"error": "The user doesn't have a subscription"}
        if response.status_code == 500:
            return {"error": "Error processing subscription cancellation"}
        return True

    ##Returns a String of the checkout url
    def create_checkout_session(self, uid=None, tier_id=None):
        data = {
            "custom_uid": uid,
            "tier_id": tier_id,
        }
        response = Utils.post(
            env=self.env,
            path="/sdk/v1/create-checkout-session",
            data=data,
            headers=self.headers,
        )

        response_json = response.json()
        return response_json

    def middleware(self, app=None):
        return self.ArchetypeMiddleware(
            app=app,
            headers=self.headers,
            app_id=self.app_id,
            secret_key=self.secret_key,
        )

    class ArchetypeMiddleware:
        def __init__(self, app, headers, app_id, secret_key):
            self.app = app
            self.headers = headers
            self.app_id = app_id
            self.secret_key = secret_key
            if "sk_test" in self.secret_key:
                self.env = "test"
            else:
                self.env = "prod"
                self.base_url = "https://test.archetype.dev"

            ##Initialize AP scheduler
            # t = BackgroundTasks()
            # t.start()
            self.client_ip = ClientIp()

        def archetype_authorize_user(
            self,
            url_apikey=None,
            body_apikey=None,
            header_apikey=None,
            client_path=None,
        ):
            data = {
                "path": client_path,
                "url_apikey": url_apikey,
                "body_apikey": body_apikey,
                "header_apikey": header_apikey,
            }
            return Utils.post(
                env=self.env, path="/sdk/v2/authorize", data=data, headers=self.headers
            )

        def __call__(self, environ, start_response):
            request = Request(environ)
            resp = Response(start_response)
            request_body = get_request_body(request)
            start_time = datetime.utcnow().timestamp()
            #self._process_response(
            #    self.app_id, resp, request, start_time, request_body
            #)
           
            url_apikey = request.args.get("apikey")
            body_apikey = request_body["apikey"] if "apikey" in request_body else None
            header_apikey = request.headers.get("apikey")

            if not header_apikey:
                res = Response(
                    json.dumps({"error": "API key not supplied in header"}),
                    mimetype="text/plain",
                    status=403,
                )
                _send_log_details(
                    app_id=self.app_id,
                    status_code=res.status_code,
                    request=request,
                    start_time=start_time,
                    request_body=get_request_body(request=request),
                )
                return res(environ, start_response)
            x = self.archetype_authorize_user(
                url_apikey=url_apikey,
                body_apikey=body_apikey,
                header_apikey=header_apikey,
                client_path=request.path,
            )

            if x.status_code < 400:

                def _start_response(status, headers, exc_info=None):
                    return start_response(status, headers, exc_info)
                
                res = self.app(environ, _start_response)
                _send_log_details(
                    app_id=self.app_id,
                    status_code=200,
                    request=request,
                    start_time=start_time,
                    request_body=get_request_body(request=request),
                )
                return res

            elif x.status_code == 400:
                res = Response(
                    json.dumps({"error": "Rate limit / Quota Exceeded"}),
                    mimetype="text/plain",
                    status=401,
                )
            elif x.status_code == 401:
                res = Response(
                    json.dumps({"error": "User doesn't have access to this endpoint"}),
                    mimetype="text/plain",
                    status=401,
                )

            elif x.status_code == 403:
                res = Response(
                    json.dumps({"error": "Invalid/Incorrect API key"}),
                    mimetype="text/plain",
                    status=403,
                )
        
            else:
                res = Response(
                    json.dumps({"error": "Authorization failed"}),
                    mimetype="text/plain",
                    status=x.status_code,
                )
            _send_log_details(
                app_id=self.app_id,
                status_code=res.status_code,
                request=request,
                start_time=start_time,
                request_body=get_request_body(request=request),
            )
            return res(environ, start_response)

        def _process_response(
            self, app_id, response, request, start_time, request_body
        ):
            request_method = request.method
            dct = {}
            dct["status_code"] = response.status_code
            dct["method"] = request_method
            dct["size"] = 0  # len(response.data)
            dct["path"] = request.path
            dct["args"] = request.args.to_dict() if request.args else {}
            dct["duration"] = datetime.utcnow().timestamp() - start_time
            dct["tier"] = "tier"
            dct["app_id"] = app_id
            dct["timestamp"] = start_time
            dct["ip"] = self.client_ip.get_client_address(request.environ)
            dct["body"] = request_body
            dct["user_id"] = (
                request.args.get("apikey") if "apikey" not in request.args else ""
            )
            dct["headers"] = (
                {k: v for k, v in request.headers.items()} if request.headers else {}
            )

            request_process = Process(target=send_details, daemon=True, args=(dct,))
            request_process.start()


def send_details(data):
    try:
        str_data = json.dumps(data)
        requests.post("https://pipeline.archetype.dev/v1/query", data=str_data)
    except Exception as e:
        print("Error sending details: " + str(e))


def get_request_body(request):
    if request.method != "GET":
        try:
            request_data = request.get_data()
            fix_bytes_value = request_data.decode("unicode_escape")
            json_data = json.loads(fix_bytes_value)
            return json_data
        except Exception as e:
            return {}
    else:
        return {}


class Utils:
    @staticmethod
    def urlify(s):
        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]", "", s)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", "-", s)

    @staticmethod
    def is_urlified(s):
        # Remove all non-word characters (everything except numbers and letters)
        t = re.sub(r"[^\w\s]", "", s)

        # Replace all runs of whitespace with a single dash
        t = re.sub(r"\s+", "-", s)

        return s == t

    @staticmethod
    def post(env="prod", path=None, data=None, headers=None):
        if env == "prod":
            req_url = base_url
        else:
            req_url = test_url
        url = f"{req_url}{path}"
        return requests.post(url, json=data, headers=headers)

    @staticmethod
    def put(path=None, data=None, headers=None):
        url = f"{base_url}{path}"
        return requests.put(url, json=data, headers=headers)

    @staticmethod
    def get(env="prod", path=None, args=None, headers=None):
        if env == "prod":
            req_url = base_url
        else:
            req_url = test_url
        url = f"{req_url}{path}"
        print(f"url: {url}")
        return requests.get(url, headers=headers)

    @staticmethod
    def is_url_readable(string):
        special_characters = '"!#$%^&*()-+?_=,<>/ "'
        if any(c in special_characters for c in string):
            return False
        else:
            return True


def fire_and_forget(f):
    def wrapper(*args, **kwargs):
        threading.Thread(target=functools.partial(f, *args, **kwargs)).start()

    return functools.wraps(f)(wrapper)



def _send_log_details(app_id, status_code, request, start_time, request_body):
    client_ip = ClientIp()
    request_method = request.method
    dct = {}
    dct["status_code"] = status_code
    dct["method"] = request_method
    dct["size"] = 0  # len(response.data)
    dct["path"] = request.path
    dct["args"] = request.args.to_dict() if request.args else {}
    dct["duration"] = datetime.utcnow().timestamp() - start_time
    dct["tier"] = "tier"
    dct["app_id"] = app_id
    dct["timestamp"] = start_time
    dct["ip"] = client_ip.get_client_address(request.environ)
    dct["body"] = request_body
    dct["user_id"] = request.args.get("apikey") if "apikey" not in request.args else ""
    dct["headers"] = (
        {k: v for k, v in request.headers.items()} if request.headers else {}
    )
    _send_details(dct)

@fire_and_forget
def _send_details(dct):
    str_data = json.dumps(dct)
    requests.post("https://pipeline.archetype.dev/v1/query", data=str_data)
