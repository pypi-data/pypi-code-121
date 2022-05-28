from abc import ABC


class Sender(ABC):
    def send_message(self, message: str) -> None:
        raise NotImplementedError("Method send_message not implemented yet")

    def send_image(self, image_path: str) -> None:
        raise NotImplementedError("Method send_image not implemented yet")

    def send_sticker(self, sticker_path: str) -> None:
        raise NotImplementedError("Method send_sticker not implemented yet")

    def send_file(self, document_path: str) -> None:
        raise NotImplementedError("Method send_file not implemented yet")
