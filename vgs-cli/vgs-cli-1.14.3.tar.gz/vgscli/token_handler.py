token = None


class CodeHandler:

    def put_code(self, api_token):
        global token
        token = api_token

    def get_code(self):
        global token
        return token
