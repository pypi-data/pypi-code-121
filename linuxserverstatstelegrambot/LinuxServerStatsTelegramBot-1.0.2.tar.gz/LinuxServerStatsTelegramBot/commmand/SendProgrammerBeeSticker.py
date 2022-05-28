from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.commmand.Command import Command


class SendProgrammerBeeSticker(Command):
    def execute(self) -> str:
        sticker_file_path = f"{DI.project_root()}/assets/794326550395748710.webp"
        return sticker_file_path
