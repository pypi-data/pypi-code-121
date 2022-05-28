class ResponseItem:
    """Response data

    Args:
        data (dict): Some kind of data.

    Examples:
        response = ResponseItem({"hello": "world", "message": "What your name?"})
        print(response.hello)
    """

    def __init__(self, data: dict):
        for name, value in data.items():
            setattr(self, name, value)
