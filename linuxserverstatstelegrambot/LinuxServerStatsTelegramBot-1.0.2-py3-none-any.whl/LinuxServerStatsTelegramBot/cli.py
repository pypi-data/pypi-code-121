import click

from LinuxServerStatsTelegramBot.DI import DI
from LinuxServerStatsTelegramBot.core.Invoker import Invoker
from LinuxServerStatsTelegramBot.sender.TelegramSender import TelegramSender


@click.command()
def notify_server_stats():
    DI.set_sender(TelegramSender())
    Invoker.send_server_stats_as_images()
    Invoker.send_server_stats_as_text()


if __name__ == "__main__":
    notify_server_stats()
