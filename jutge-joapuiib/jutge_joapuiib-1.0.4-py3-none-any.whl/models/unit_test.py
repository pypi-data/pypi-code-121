class UnitTest:
    def __init__(self, name, _dict={}):
        self.name = name
        self.result = {}

        if not _dict:
            _dict = {}

        self.source = _dict.get("source", None)
        self.input = _dict.get("input", None)
        self.expected_output = _dict.get("output", None)
        self.expected_stderr = _dict.get("stderr", None)
        self.force = _dict.get("force", False)

        self.output = ""
        self.stderr = ""
        self.colored_output = None
        self.colored_expected_output = None

        self.init = _dict.get("init", [])
        if not isinstance(self.init, list):
            self.init = [self.init]

        self.post = _dict.get("post", [])
        if not isinstance(self.post, list):
            self.post = [self.post]

        self.clean = _dict.get("clean", [])
        if not isinstance(self.clean, list):
            self.clean = [self.clean]

        self.tests = []
        for test_name, test in _dict.get("tests", {}).items():
            self.tests.append(UnitTest(test_name, test))

    def set_status(self, status):
        self.status = status
        self.result["status"] = status.name

    def set_output(self, output):
        self.output = output
        self.result["output"] = output

    def get_result(self):
        self.result["name"] = self.name
        if self.source:
            self.result["source"] = self.source
        if self.input:
            self.result["input"] = self.input

        output = self.output
        expected_output = self.expected_output

        if self.expected_stderr:
            output = self.stderr
            expected_output = self.expected_stderr

        if expected_output:
            self.result["expected_output"] = expected_output
        if output:
            self.result["output"] = output

        if self.tests:
            self.result["tests"] = []
            for unit_test in self.tests:
                self.result["tests"].append(unit_test.get_result())

        return self.result
