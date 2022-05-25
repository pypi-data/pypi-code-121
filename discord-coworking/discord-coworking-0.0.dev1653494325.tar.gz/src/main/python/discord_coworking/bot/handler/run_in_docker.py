import emoji
from datetime import datetime
import asyncio
from discord import Message, Client
import os
import docker
from docker.types import Mount

import re

from discord_coworking.bot import MessageHandler
from dataclasses import dataclass, field


@dataclass()
class DockerRun:
    language: str
    code: str
    docker_client: docker.DockerClient = field(default_factory=docker.from_env)

    loading_emoji = emoji.EMOJI_ALIAS_UNICODE[':hourglass:']
    success_emoji = emoji.EMOJI_ALIAS_UNICODE[':white_check_mark:']
    error_emoji = emoji.EMOJI_ALIAS_UNICODE[':x:']
    default_emoji = emoji.EMOJI_ALIAS_UNICODE[':gear:']

    emoji = {
        'python': emoji.EMOJI_ALIAS_UNICODE[':snake:'],
        'java': emoji.EMOJI_ALIAS_UNICODE[':coffee:'],
        'js': emoji.EMOJI_ALIAS_UNICODE[':poop:'],
        'ts': emoji.EMOJI_ALIAS_UNICODE[':sauropod:'],
        'php': emoji.EMOJI_ALIAS_UNICODE[':elephant:'],
        'c': emoji.EMOJI_ALIAS_UNICODE[':regional_indicator_c:'],
        'cpp': emoji.EMOJI_ALIAS_UNICODE[':rat:'],
        'rust': emoji.EMOJI_ALIAS_UNICODE[':crab:'],
        'sh': emoji.EMOJI_ALIAS_UNICODE[':shell:'],
        'bash': emoji.EMOJI_ALIAS_UNICODE[':computer:'],
        'go': emoji.EMOJI_ALIAS_UNICODE[':chipmunk:'],
        'lua': emoji.EMOJI_ALIAS_UNICODE[':new_moon:'],
        'ruby': emoji.EMOJI_ALIAS_UNICODE[':diamonds:'],
        'lisp': emoji.EMOJI_ALIAS_UNICODE[':alien:'],
        'perl': emoji.EMOJI_ALIAS_UNICODE[':onion:'],
        'r': emoji.EMOJI_ALIAS_UNICODE[':regional_indicator_r:'],
        'julia': emoji.EMOJI_ALIAS_UNICODE[':regional_indicator_j:'],
        'kotlin': emoji.EMOJI_ALIAS_UNICODE[':regional_indicator_k:'],
    }

    aliases = {
        'c++': 'cpp',
        'javascript': 'js',
        'typescript': 'ts',
    }

    images = {
        'python': 'python:3.10',
        'java': 'openjdk:11',
        'js': 'node:lts',
        'ts': 'hayd/deno',
        'php': 'php',
        'c': 'gcc',
        'cpp': 'gcc',
        'rust': 'rust',
        'sh': 'fedora',
        'bash': 'fedora',
        'go': 'golang',
        'lua': 'woahbase/alpine-lua',
        'ruby': 'ruby',
        'haskell': 'haskell',
        'lisp': 'daewok/lisp-devel',
        'perl': 'perl',
        'r': 'r-base',
        'julia': 'julia',
        'kotlin': 'zenika/kotlin',
    }

    commands = {
        'python': 'python {}',
        'java': 'java {}',
        'js': 'node {}',
        'ts': 'deno run -q {}',
        'php': 'php {}',
        'c': '/bin/bash -c "gcc {} -o /tmp/a.out;/tmp/a.out"',
        'cpp': '/bin/bash -c "gcc -x c++ {} -lstdc++ -o /tmp/a.out;/tmp/a.out"',
        'rust': '/bin/bash -c "rustc {} -o /tmp/a.out;/tmp/a.out"',
        'sh': '/bin/sh {}',
        'bash': '/bin/bash {}',
        'go': 'go run {}',
        'lua': 'lua {}',
        'ruby': 'ruby {}',
        'haskell': 'runghc {}',
        'lisp': 'sbcl --script {}',
        'perl': 'perl {}',
        'r': 'Rscript {}',
        'julia': 'julia {}',
        'kotlin': 'kotlinc -script  {}',
    }

    scripts = {
        'python': 'script.py',
        'java': 'Script.java',
        'js': 'script.js',
        'ts': 'script.ts',
        'php': 'script.php',
        'c': 'script.c',
        'cpp': 'script.cpp',
        'rust': 'script.rs',
        'sh': 'script.sh',
        'bash': 'script.sh',
        'go': 'script.go',
        'lua': 'script.lua',
        'ruby': 'script.rb',
        'haskell': 'script.hs',
        'lisp': 'script.lisp',
        'perl': 'script.pl',
        'r': 'script.r',
        'julia': 'julia.jl',
        'kotlin': 'script.kts',
    }

    async def __call__(self, client: Client, message: Message):
        try:
            language = self.aliases.get(self.language, self.language)
            image = self.images.get(language)
            command = self.commands.get(language)
            script = self.scripts.get(language)
            if None in [image, command, script]:
                return
            await message.add_reaction(self.emoji.get(language, self.default_emoji))
            volume = f'/tmp/discord-coworking-{message.id}/'
            os.mkdir(volume)
            with open(os.path.join(volume, script), 'w+') as output:
                output.write(self.code)
            container = self.docker_client.containers.run(
                image,
                command.format(os.path.join(volume, script)),
                auto_remove=False,
                mounts=[
                    Mount(source=volume, target=volume, type='bind')
                ],
                detach=True,
                network_mode='none',
                mem_limit='256m',
                nano_cpus=int(0.25 * 10 ** 9),
            )
            await message.add_reaction(self.loading_emoji)
            started_at = datetime.now()
            running = True
            while running:
                try:
                    result = container.wait(timeout=0.01)
                    running = False
                except:
                    diff = datetime.now() - started_at
                    if diff.seconds >= 10:
                        container.remove(force=True)
                        raise Exception('Timeout')
                    await asyncio.sleep(0.5)
            stdout = container.logs()
            container.remove()
            if result['StatusCode'] != 0:
                raise Exception(stdout.decode())
            await message.add_reaction(self.success_emoji)
            await message.reply(stdout.decode())
        except Exception as ex:
            await message.add_reaction(self.error_emoji)
            await message.reply(f'```{ex.args[0]}```')
        finally:
            await message.remove_reaction(self.loading_emoji, client.user)


class RunCodeInDocker(MessageHandler):
    pattern = re.compile('```(?P<language>[a-zA-Z0-9+#-]+)\\n(?P<code>[^`]*)```')

    def accept(self, message: Message) -> bool:
        match = self.pattern.findall(message.clean_content)
        return bool(match)

    async def handle(self, client: Client, message: Message):
        for match in self.pattern.findall(message.clean_content):
            language, code = match
            run = DockerRun(language=language.lower(), code=code)
            asyncio.ensure_future(run(client, message))
