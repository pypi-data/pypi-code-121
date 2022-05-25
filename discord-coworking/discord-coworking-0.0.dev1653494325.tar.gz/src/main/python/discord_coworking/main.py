import asyncio
import tempfile
import emoji
import shlex
import json
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import argparse
import asyncio
import io
import logging.config
import os
import pickle
from asyncio.tasks import Task

import discord

from discord.message import Message

from discord_coworking.bot.handler import MessageHandlerNode
from discord_coworking.command.api import Result
from discord_coworking.command.category import DeleteCategory
from discord_coworking.command.coworking import CreateOrganization
from discord_coworking.command.guild import GuildPredicate
from discord_coworking.command.predicate import ANY
from discord_coworking.command.role import DeleteRole
from discord_coworking.command.text_channel import DeleteTextChannel
from discord_coworking.command.voice_channel import DeleteVoiceChannel
from discord_coworking.bot import CoworkingBot, StartByMentioningMe
from discord_coworking.bot.handler.run_in_docker import RunCodeInDocker

log_level_map = {
    'd': 'DEBUG',
    'debug': 'DEBUG',
    'i': 'INFO',
    'info': 'INFO',
    'w': 'WARNING',
    'warning': 'WARNING',
    'c': 'CRITICAL',
    'critical': 'CRITICAL',
}


def create_parser(bot_command=True, token_param=True, log_level_param=True,
                  client_factory_param=True) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='discord-coworking',
        description='Discord coworking server management toolkit',
    )
    if token_param:
        parser.add_argument(
            '--token',
            help='Discord Bot Token, environment DISCORD_TOKEN',
            **default_env('DISCORD_TOKEN', str, None),
        )
    parser.add_argument(
        '--guild',
        help='Guild ID',
        **default_env('GUILD_ID', lambda it: GuildPredicate.create(id=int(it)), ANY)
    )
    if log_level_param:
        parser.add_argument(
            '--log-level',
            help='Log level',
            default=os.environ.get('LOG_LEVEL', 'i'),
            choices=list(log_level_map.keys()),
            type=lambda it: log_level_map.get(it, logging.INFO),
        )
    if client_factory_param:
        parser.set_defaults(
            client_factory=discord.Client,
        )
    subparsers = parser.add_subparsers(
        title='sub command',
    )
    undo = subparsers.add_parser(
        'undo',
    )
    undo.add_argument(
        '-I', '-i', '--input',
        help='Serialized result file',
        type=argparse.FileType('rb'),
    )
    undo.set_defaults(command=undo_command)
    if bot_command:
        bot = subparsers.add_parser(
            'bot',
        )
        bot.set_defaults(
            client_factory=CoworkingBot,
            command=run_bot,
        )
    create_organization_commands = {
        'create-open-organization': CreateOrganization.open_organization,
        'create-private-organization': CreateOrganization.private_organization,
    }
    for name, factory in create_organization_commands.items():
        create_organization = subparsers.add_parser(
            name,
        )
        create_organization.add_argument(
            '-o', '-O', '--output',
            dest='output',
            default='a.out',
            type=argparse.FileType('wb+'),
        )
        create_organization.add_argument(
            '--name',
            required=True,
        )
        create_organization.set_defaults(
            command=discord_command,
            command_factory=factory,
        )
    delete_commands = {
        'delete-category': DeleteCategory,
        'delete-voice-channel': DeleteVoiceChannel,
        'delete-text-channel': DeleteTextChannel,
        'delete-role': DeleteRole,
    }
    for name, factory in delete_commands.items():
        create_organization = subparsers.add_parser(
            name,
        )
        create_organization.add_argument(
            '-O', '-o', '--output',
            dest='output',
            default='a.out',
            type=argparse.FileType('wb+'),
        )
        create_organization.set_defaults(
            command=discord_command,
            command_factory=factory,
        )
    list_commands = {
        'list-guild': None,
    }
    for name, _ in list_commands.items():
        command = subparsers.add_parser(
            name,
        )
        command.set_defaults(
            command=list_command,
        )
    return parser


def config_log(log_level):
    logging.basicConfig(level=log_level)
    logging.info(f'Log level set to {log_level}')


async def run(token: str, client_factory, command, log_level, **params):
    config_log(log_level)
    client = client_factory()
    loop = asyncio.get_event_loop()
    client_task = loop.create_task(client.start(token))
    await client.wait_until_ready()
    await command(client, **params, client_task=client_task)


async def list_command(client: discord.Client, **params):
    for guild in client.guilds:
        print(f'"{guild.name}" ({guild.id})')


async def print_handler(client, message: Message):
    print(message)
    print(message.mentions)
    print(message.content)
    print(message.clean_content)


async def reply_handler(client, message: Message):
    await message.reply(message.clean_content)


def error(err):
    raise Exception(err)


def exit(status=0, message=None):
    if status == 0:
        return
    raise Exception(message)


class RunAsCommand():
    tool_emoji = emoji.EMOJI_ALIAS_UNICODE[':hammer_and_wrench:']
    loading_emoji = emoji.EMOJI_ALIAS_UNICODE[':hourglass:']
    success_emoji = emoji.EMOJI_ALIAS_UNICODE[':white_check_mark:']
    error_emoji = emoji.EMOJI_ALIAS_UNICODE[':x:']

    def __init__(self):
        self.parser = create_parser(bot_command=False, token_param=False, log_level_param=False,
                                    client_factory_param=False)
        self.parser.error = error
        self.parser.exit = exit

    async def __call__(self, client: discord.Client, message: Message):
        if not message.author.guild_permissions.administrator:
            await message.reply("Sorry I can't help you with that, ask to an administrator")
            return
        await message.add_reaction(self.tool_emoji)
        args = shlex.split(message.clean_content)
        try:
            input_file = None
            for attachment in message.attachments:
                _, input_file = tempfile.mkstemp()
                with open(input_file, 'wb+') as attachment_output:
                    attachment_output.write(await attachment.read())
                break
            if input_file:
                args += [f'--input={input_file}']
            namespace = self.parser.parse_args([f"--guild={message.guild.id}"] + args[1:])
            params = vars(namespace)
            command = params.pop('command')
            await message.add_reaction(self.loading_emoji)
            await command(client=client, **params)
            files = []
            if 'output' in namespace:
                namespace.output.close()
                file = os.path.abspath(namespace.output.name)
                files.append(discord.File(fp=file, filename=os.path.basename(file)))
            await message.reply('=)', files=files)
            await message.add_reaction(self.success_emoji)
        except KeyError:
            await message.reply(self.parser.format_help())
        except Exception as ex:
            await message.add_reaction(self.error_emoji)
            await message.reply(str(ex))
        finally:
            await message.remove_reaction(self.loading_emoji, client.user)


async def run_bot(client: CoworkingBot, client_task: Task, **params):
    client.message_handler.handlers.extend([
        RunCodeInDocker(),
        MessageHandlerNode(RunAsCommand(), StartByMentioningMe(client)),
    ])
    await client_task


async def undo_command(client: discord.Client, input: io.BufferedReader, **params):
    undoable = pickle.load(input)
    if not isinstance(undoable, (Result,)):
        raise Exception('The input file is not a result')
    await undoable.undo(client)


async def discord_command(client: discord.Client, command_factory, output: io.BufferedWriter, **parameters):
    command = command_factory(**parameters)
    logging.info(f'Running command {command}')
    pickle.dump(await command.do(client), output)


def default_env(name, type, default):
    env_value = os.environ.get(name, None)
    return {
        'default': default if env_value is None else type(env_value),
        'required': env_value is None and default is None,
        'type': type,
    }


async def main():
    parser = create_parser()
    namespace = parser.parse_args()
    return await run(**vars(namespace))


try:
    cpu_count = multiprocessing.cpu_count()
    thread_pool = ThreadPoolExecutor(cpu_count)
    loop = asyncio.get_event_loop()
    loop.set_default_executor(thread_pool)
    loop.run_until_complete(main())
except KeyboardInterrupt:
    asyncio.get_event_loop().close()
