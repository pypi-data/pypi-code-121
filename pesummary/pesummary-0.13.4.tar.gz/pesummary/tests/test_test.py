class TestClass:
    @classmethod
    def setup_class(cls):
        print("starting class: {} setup".format(cls.__name__))

    @classmethod
    def teardown_class(cls):
        print("starting class: {} execution".format(cls.__name__))

    def setup_method(self, method):
        print("starting execution of tc: {}".format(method.__name__))

    def teardown_method(self, method):
        print("starting execution of tc: {}".format(method.__name__))

    def test_tc1(self):
        assert 1==2

    def test_tc2(self):
        assert 1==2
