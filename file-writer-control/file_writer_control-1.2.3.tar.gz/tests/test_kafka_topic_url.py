import pytest

from file_writer_control.KafkaTopicUrl import KafkaTopicUrl


def test_success_1():
    url_obj = KafkaTopicUrl("kafka://addr:9012/hello_12")
    assert url_obj.host_port == "addr:9012"
    assert url_obj.topic == "hello_12"


def test_success_2():
    url_obj = KafkaTopicUrl("kafka://addr/hello_12")
    assert url_obj.host_port == "addr:9092"
    assert url_obj.topic == "hello_12"


def test_success_3():
    url_obj = KafkaTopicUrl("addr:9012/hello_12")
    assert url_obj.host_port == "addr:9012"
    assert url_obj.topic == "hello_12"


def test_success_4():
    url_obj = KafkaTopicUrl("addr.se:9012/hello_12")
    assert url_obj.host_port == "addr.se:9012"
    assert url_obj.topic == "hello_12"


def test_success_5():
    url_obj = KafkaTopicUrl("192.168.1.21:9012/hello_12")
    assert url_obj.host_port == "192.168.1.21:9012"
    assert url_obj.topic == "hello_12"


def test_failure_1():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("kafka://:9012/hello_12")


def test_failure_2():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("kafka://what.com/")


def test_failure_3():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("kafka://what.com")


def test_failure_4():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("kafka:/what.com:124/hej")


def test_failure_5():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("kafkaaa://what.com:124/hej")


def test_failure_6():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("//what.com:124/hej")


def test_failure_7():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("kafka://what.com:sfa/hej")


def test_failure_8():
    with pytest.raises(RuntimeError):
        KafkaTopicUrl("kafka://what.com:1234/hej/again")
