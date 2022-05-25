class BasicFile:
    def __init__(self, filename: str, content_type: str, base64_content: str):
        self.filename = filename
        self.content_type = content_type
        self.base64_content = base64_content
