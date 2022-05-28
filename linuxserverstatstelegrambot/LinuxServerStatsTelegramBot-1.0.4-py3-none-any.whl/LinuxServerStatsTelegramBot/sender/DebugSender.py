from LinuxServerStatsTelegramBot.sender.Sender import Sender


class DebugSender(Sender):
    def __init__(self):
        pass

    def send_message(self, message: str) -> None:
        print(f"Executing send_message with message = {message}")

    def send_image(self, image_path: str) -> None:
        print(f"Executing send_image with image_path = {image_path}")

    def send_sticker(self, sticker_path: str) -> None:
        print(f"Executing send_sticker with sticker_path = {sticker_path}")

    def send_file(self, document_path: str):
        print(f"Executing send_file with document_path = {document_path}")
