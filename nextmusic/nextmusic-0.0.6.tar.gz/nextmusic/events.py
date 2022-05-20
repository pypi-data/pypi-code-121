import wavelink
from nextcord.ext import commands

from ._classes import Loop
from .errors import (InvalidLoopMode, MustBeSameChannel, NotConnectedToVoice,
                     NotEnoughSong, NothingIsPlaying, PlayerNotConnected)
from .player import NextPlayer
from .ext import Commands
from rich import print
from motor.motor_asyncio import AsyncIOMotorClient
from .music import NextPlayer


class MusicEvents(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        try:
            self.cluster = AsyncIOMotorClient(self.bot.mongo_url)
            self.db = self.cluster['main']
            self._247 = self.db['247vcs']
        except:
            self.cluster = AsyncIOMotorClient('nourl')

    async def handle_end_stuck_exception(
        self, player: NextPlayer, track: wavelink.abc.Playable
    ):
        if player.loop == Loop.CURRENT:
            return await player.play(track)

        if player.loop == Loop.PLAYLIST:
            await player.queue.put(track)

        player._source = None
        await player.do_next()

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player, track, *args, **kwargs):
        self.bot.dispatch("nextmusic_track_end", player, track)
        await self.handle_end_stuck_exception(player, track)

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, player, track, *args, **kwargs):
        self.bot.dispatch("nextmusic_track_exception", player, track)
        await self.handle_end_stuck_exception(player, track)

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, player, track, *args, **kwargs):
        self.bot.dispatch("nextmusic_track_stuck", player, track)
        await self.handle_end_stuck_exception(player, track)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'[ Nextmusic ] INFO - {self.bot.user} is now online')
        print(f'[ Nextmusic ] INFO - [link=https://araki.social/support]Support server[/link] - https://araki.social/support')
        print(f'[ Nextmusic ] INFO - Created by Pranoy#0140')
        try:
            find = self._247.find({'vcid': {'$gt': 0}})
            async for ids in find:
                id = ids['vcid']
                guild = ids['guild']
                fguild = self.bot.get_guild(guild)
                channel = await self.bot.fetch_channel(id)
                # try:
                #     await channel.connect()
                # except:
                #     pass
                try:
                    player: NextPlayer = await channel.connect(cls=NextPlayer)
                    self.bot.dispatch("nextmusic_player_connect", player)
                except:
                    pass
                try:
                    await fguild.me.edit(deafen=True)
                except:
                    pass
        except:
            pass



    # @commands.Cog.listener()
    # async def on_command_error(self, ctx, error):
    #     errors = (
    #         InvalidLoopMode,
    #         MustBeSameChannel,
    #         NotConnectedToVoice,
    #         PlayerNotConnected,
    #         NothingIsPlaying,
    #         NotEnoughSong,
    #     )

    #     if isinstance(error, errors):
    #         await ctx.send(error)
    #     else:
    #         pass
