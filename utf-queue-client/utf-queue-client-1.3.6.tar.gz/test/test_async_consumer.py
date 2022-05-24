from utf_queue_client.clients.async_consumer import AsyncConsumerBase



def test_sanitize_url():
    params = [
        ("amqp://www.ni.com", "amqp://www.ni.com"),
        ("amqps://utfsilabs:password1234@www.ni.com", "amqps://utfsilabs:******@www.ni.com"),
    ]
    for url, display_url in params:
        sanitized_url = AsyncConsumerBase.sanitize_url_for_display(url)
        assert sanitized_url == display_url