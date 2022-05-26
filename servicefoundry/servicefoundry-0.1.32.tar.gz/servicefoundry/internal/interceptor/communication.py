import json

INVOKE_OP_CODE = "invoke:"
RESPONSE_OP_CODE = "response:"
ERROR_OP_CODE = "error:"
ACK_OP_CODE = "ack:"
DEPENDENCIES_OP_CODE = "dependency:"
FUNCTION_OP_CODE = "function:"
CLOSE_OP_CODE = "close:"


class Invoke:
    def __init__(self, function, payload):
        self.function = function
        self.payload = payload


class Response:
    def __init__(self, output):
        self.output = output


class ErrorResponse:
    def __init__(self, message, traceback):
        self.message = message
        self.traceback = traceback


class Close(ErrorResponse):
    pass


class Ack:
    pass


class Dependencies:
    pass


class Function:
    pass


class InvokeException(Exception):
    def __init__(self, message, traceback):
        super(InvokeException, self).__init__()
        self.message = message
        self.traceback = traceback

    def __str__(self):
        return self.message


class CloseException(Exception):
    def __init__(self, message, traceback):
        super(CloseException, self).__init__()
        self.message = message
        self.traceback = traceback

    def __str__(self):
        return self.message


class Communication:
    def __init__(self, infile, outfile):
        self.infile = infile
        self.outfile = outfile

    def read_input_msg(self):
        line = self.infile.readline()
        if line.startswith(INVOKE_OP_CODE):
            payload = json.loads(line[len(INVOKE_OP_CODE) :])
            return Invoke(function=payload["function"], payload=payload["payload"])
        elif line.startswith(RESPONSE_OP_CODE):
            payload = json.loads(line[len(RESPONSE_OP_CODE) :])
            return Response(output=payload["response"])
        elif line.startswith(ERROR_OP_CODE):
            payload = json.loads(line[len(ERROR_OP_CODE) :])
            raise InvokeException(payload["msg"], payload["traceback"])
        elif line.startswith(DEPENDENCIES_OP_CODE):
            return Dependencies()
        elif line.startswith(ACK_OP_CODE):
            return Ack()
        elif line.startswith(FUNCTION_OP_CODE):
            return Function()
        elif line.startswith(CLOSE_OP_CODE):
            payload = json.loads(line[len(CLOSE_OP_CODE) :])
            raise CloseException(payload["msg"], payload["traceback"])
        else:
            self.write_exception(f"Incorrect op code.")

    def read_response(self):
        response = self.read_input_msg()
        if isinstance(response, Response):
            return response.output
        raise RuntimeError(
            f"Unexpected response type {response.__class__}. Was expecting response or error."
        )

    def read_ack(self):
        response = self.read_input_msg()
        if isinstance(response, Ack):
            return
        raise RuntimeError(
            f"Unexpected response type {response.__class__}. Was expecting ack."
        )

    def write_ack(self):
        print(f"{ACK_OP_CODE}", file=self.outfile)

    def write_function(self):
        print(f"{FUNCTION_OP_CODE}", file=self.outfile)

    def write_invoke(self, function_name, **kwargs):
        invoke = {"function": function_name, "payload": kwargs}
        print(f"{INVOKE_OP_CODE}{json.dumps(invoke)}", file=self.outfile)

    def write_dependencies(self):
        print(f"{DEPENDENCIES_OP_CODE}", file=self.outfile)

    def write_response(self, res):
        res = {"response": res}
        print(f"{RESPONSE_OP_CODE}{json.dumps(res)}", file=self.outfile)

    def write_exception(self, msg, traceback=None):
        res = {"msg": msg, "traceback": traceback}
        print(f"{ERROR_OP_CODE}{json.dumps(res)}", file=self.outfile)

    def write_close(self, msg, traceback=None):
        res = {"msg": msg, "traceback": traceback}
        print(f"{CLOSE_OP_CODE}{json.dumps(res)}", file=self.outfile)

    def close(self):
        self.infile.close()
        self.outfile.close()
