DEBUG = False

class ResponseHandler:
    def __handle_failure(self, resp, url):
        code = resp.status_code

        if code in [503, 500, 409, 404, 400]:
            raise Exception('Method: '+ self.method +", Server Error: " + str(code) +  " Message: "+ resp.text +  " URL: ", str(url), ' payload: ', self.payload)

        if code == 401:
            raise Exception("URL: ", url ," Method: ", self.method, ", Server returned 401: Unauthorized. Please check username or password.")


        json_data = resp.json()
        error_message = json_data["error"] + "--" + json_data["error_description"]
        raise Exception("Method: "+ self.method +" Error: " + str(code) + " \n for URL:" + str(url) + " \n Response: " +  error_message)


    def __init__(self, urlObject, method = None, payload=None):
        self.URL = urlObject
        self.method = method
        self.payload = payload

    def handleResponse(self, response):
        self.response = response
        self.status = response.status_code
        return self

    def verify(self):
        if self.isOk():
            return self

    def isOk(self):
        if self.status >= 200 and self.status <=208:
            return True
        else:
            self.__handle_failure(self.response, self.URL)

        return self

    def ok(self):
        return self.status >= 200 and self.status <= 208

    def resp(self):
        return self.response

    def response(self):
        return self.response
