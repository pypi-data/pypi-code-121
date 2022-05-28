from datetime import datetime
from zipfile import ZipFile
from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.commmand.Command import Command
from LinuxServerStatsTelegramBot.commmand.ConvertTextToImage import ConvertTextToImage
from LinuxServerStatsTelegramBot.commmand.CpuStats import CpuStats
from LinuxServerStatsTelegramBot.commmand.SendProgrammerBeeSticker import SendProgrammerBeeSticker

from LinuxServerStatsTelegramBot.commmand.CronStats import CronStats
from LinuxServerStatsTelegramBot.commmand.DiskStats import DiskStats
from LinuxServerStatsTelegramBot.commmand.DockerStats import DockerStats
from LinuxServerStatsTelegramBot.commmand.MemoryStats import MemoryStats
from LinuxServerStatsTelegramBot.commmand.DateAndLocation import DateAndLocation
from LinuxServerStatsTelegramBot.commmand.ServersHealth import ServersHealth
from LinuxServerStatsTelegramBot.commmand.CleanMemory import CleanMemory


class Invoker:
    @staticmethod
    def send_server_stats_as_images():
        Invoker.send_sticker()
        Invoker.send_data_as_image(DateAndLocation())
        Invoker.send_data_as_image(MemoryStats())
        Invoker.send_data_as_image(CpuStats())
        Invoker.send_data_as_image(DiskStats())
        Invoker.send_data_as_image(DockerStats())
        Invoker.send_data_as_image(CronStats())
        Invoker.send_data_as_image(ServersHealth())
        Invoker.send_data_as_image(CleanMemory())

    @staticmethod
    def send_server_stats_as_text():
        commands = [DateAndLocation(), MemoryStats(), CpuStats(), DiskStats(),
                    DockerStats(), CronStats(), ServersHealth(), CleanMemory()]
        Invoker.zip_and_send(commands)

    @staticmethod
    def zip_and_send(commands: list[Command]):
        sender = DI.get_sender()
        files: list = []
        for command in commands:
            command_name = command.__class__.__name__
            data = command.execute()
            cmd_file_path = f"/tmp/{command_name}.txt"
            files.append(cmd_file_path)
            with open(cmd_file_path, "w") as output_file:
                output_file.write(data)

        current_date_time = datetime.today().strftime("%Y%m%d_%H%M%S")
        zip_file_path = f"/tmp/reports_{current_date_time}.zip"
        with ZipFile(zip_file_path, "w") as zipFile:
            for file in files:
                zipFile.write(file)

        sender.send_file(zip_file_path)

    @staticmethod
    def send_data_as_image(command: Command):
        command_name = command.__class__.__name__
        sender = DI.get_sender()
        data = command.execute()
        image_path = f"/tmp/{command_name}.png"
        ConvertTextToImage(data=data, image_path=image_path).execute()
        sender.send_image(image_path=image_path)

    @staticmethod
    def send_sticker():
        sticker_path = SendProgrammerBeeSticker().execute()
        sender = DI.get_sender()
        sender.send_sticker(sticker_path=sticker_path)
