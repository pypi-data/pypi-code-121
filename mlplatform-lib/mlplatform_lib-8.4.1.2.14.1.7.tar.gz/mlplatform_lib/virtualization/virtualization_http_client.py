class VirtualizationRequestException(Exception):
    status_code = 200

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

class VirtualizationRequestType(Enum):
    CREATE = 0
    READ = 1
    UPDATE = 2
    DELETE = 3
    DOWNLOAD = 4
    READ_WITH_FORM_DATA = 5

@dataclass
class VirtualizationRequestResult:
    data: Optional[Union[Dict, List[Dict], bytes]]
    content: Optional[str]
    status_code: Optional[int]

class VirtualizationHttpClient:
    def __init__(self, virtualization_addr, api_client: ApiClient):
        self.url = virtualization_addr + "/hyperdata/web-service"
        self.api_client = api_client

    def send_request(
        self,
        service: str,
        rest: Optional[dict],
        query: Optional[dict],
        data: Optional[dict],
        request_type: VirtualizationRequestType,
    ) -> VirtualizationRequestResult:
        headers = {
            "Content-Type": "application/json",
        }

        if rest is None:
            rest = {}

        if query is None:
            query = {}

        if data is None:
            data = {}

        if service == "dataObjectTuple":
            headers["doType"] = "inferenceResult"

        if request_type == VirtualizationRequestType.DOWNLOAD:
            headers["Content-Type"] = "application/octet-stream"

        for key, val in rest.items():
            url = url + "/" + str(key) + "/" + str(val)
        if service != "" and service is not None:
            url = url + "/" + service

        if len(query) != 0:
            url += "?"
            for idx, (key, val) in enumerate(query.items()):
                if idx != 0:
                    url += "&"
                url = url + str(key) + "=" + str(val)

        if request_type == VirtualizationRequestType.READ or request_type == VirtualizationRequestType.DOWNLOAD:
            response = requests.get(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == VirtualizationRequestType.CREATE:
            response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == VirtualizationRequestType.UPDATE:
            response = requests.put(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == VirtualizationRequestType.DELETE:
            response = requests.delete(url, headers=headers, data=json.dumps(data), verify=False)
        elif request_type == VirtualizationRequestType.READ_WITH_FORM_DATA:
            response = requests.get(url, headers=headers, data=json.dumps(data), verify=False)
        else:
            return VirtualizationRequestResult(None, None, None)

        if response.status_code == 200:
            if request_type == VirtualizationRequestType.DOWNLOAD:
                return VirtualizationRequestResult(response.content, None, response.status_code)
            else:
                return VirtualizationRequestResult(
                    response.json(), response.content.decode(), response.status_code
                )
        else:
            print(response.content.decode())
            print(
                (
                    f"cannot connect to {self.url}. "
                    f"virtualization server returns status code {response.status_code}"
                )
            )
            raise VirtualizationRequestException(response.content.decode(), response.status_code)

    def download_unstructured(self, do_id:str):
        print("Start download_unstructured in Virtualization Http Client")
        return self.send_request(
            "download/ozone/unstructured",
            {"dataobjects": do_id},
            {"fileName":do_id,"regex":"","dateStart":"","dateEnd":""},
            {},
            VirtualizationRequestType.READ,
        )