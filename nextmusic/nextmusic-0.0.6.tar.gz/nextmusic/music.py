import asyncio
import nextcord
import async_timeout
import wavelink
from nextcord import ClientException
from nextcord.ext import commands
from wavelink import (LavalinkException, LoadTrackError, SoundCloudTrack,
                      YouTubeMusicTrack, YouTubePlaylist, YouTubeTrack)
from wavelink.ext import spotify
from rich import print
from wavelink.ext.spotify import SpotifyTrack
from ._classes import Provider
from .checks import voice_channel_player, voice_connected
from .errors import MustBeSameChannel
from .paginator import Paginator
from .player import NextPlayer
from .ext import Commands
import motor
from motor.motor_asyncio import AsyncIOMotorClient


class Music(commands.Cog):
    """Music commands"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        try:
            self.cluster = AsyncIOMotorClient(self.bot.mongo_url)
            self.db = self.cluster['main']
            self._247 = self.db['247vcs']
        except:
            self.cluster = AsyncIOMotorClient('nourl')
        self.bot.loop.create_task(self.start_nodes())

    def get_nodes(self):
        return sorted(wavelink.NodePool._nodes.values(), key=lambda n: len(n.players))

    def musicEmb(self, author, description):
        embed = nextcord.Embed(description=description, colour=Commands.embed_colour(self))
        embed.set_footer(text='Powered by Nextmusic')
        embed.set_author(name=author)
        return embed

    async def play_track(self, ctx: commands.Context, query: str, provider=None):
        player: NextPlayer = ctx.voice_client

        if ctx.author.voice.channel.id != player.channel.id:
            raise MustBeSameChannel(
                "You must be in the same voice channel as the player."
            )

        track_providers = {
            "yt": YouTubeTrack,
            "ytpl": YouTubePlaylist,
            "ytmusic": YouTubeMusicTrack,
            "soundcloud": SoundCloudTrack,
            "spotify": SpotifyTrack,
        }

        query = query.strip("<>")
        msg = await ctx.send(f"Searching for `{query}` :mag_right:")

        track_provider = provider if provider else player.track_provider

        if track_provider == "yt" and "playlist" in query:
            provider = "ytpl"

        provider: Provider = (
            track_providers.get(provider)
            if provider
            else track_providers.get(player.track_provider)
        )

        nodes = self.get_nodes()
        tracks = list()

        for node in nodes:
            try:
                with async_timeout.timeout(20):
                    tracks = await provider.search(query, node=node)
                    break
            except asyncio.TimeoutError:
                self.bot.dispatch("nextmusic_node_fail", node)
                wavelink.NodePool._nodes.pop(node.identifier)
                continue
            except (LavalinkException, LoadTrackError):
                continue

        if not tracks:
            return await msg.edit("No song/track found with given query.")

        if isinstance(tracks, YouTubePlaylist):
            tracks = tracks.tracks
            for track in tracks:
                await player.queue.put(track)

            await msg.edit(content=f"Added `{len(tracks)}` songs to queue. ")
        else:
            track = tracks[0]

            await msg.edit(content=f"Added `{track.title}` to queue. ")
            await player.queue.put(track)

        if not player.is_playing():
            await player.do_next()

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        spotify_credential = getattr(
            self.bot, "spotify_credentials", {"client_id": "", "client_secret": ""}
        )

        for config in self.bot.lavalink_nodes:
            try:
                node: wavelink.Node = await wavelink.NodePool.create_node(
                    bot=self.bot,
                    **config,
                    spotify_client=spotify.SpotifyClient(**spotify_credential),
                )
                print(f'[ Nextmusic ] INFO - Node is created - {node.identifier}')
                


            except Exception:
                print(
                    f"[nextmusic] ERROR - Failed to create node {config['host']}:{config['port']}"
                )

    @commands.command(aliases=["join", "j"])
    @voice_connected()
    async def connect(self, ctx: commands.Context):
        """Connect the player"""
        if ctx.voice_client:
            return

        msg = await ctx.send(f"Connecting to **`{ctx.author.voice.channel}`**")

        try:
            player: NextPlayer = await ctx.author.voice.channel.connect(cls=NextPlayer)
            self.bot.dispatch("nextmusic_player_connect", player)
        except (asyncio.TimeoutError, ClientException):
            return await msg.edit(content="Failed to connect to voice channel.")

        player.bound_channel = ctx.channel
        player.bot = self.bot

        await msg.edit(content=f"Connected to **`{player.channel.name}`**")

    

    @commands.group(aliases=["p"], invoke_without_command=True)
    @voice_connected()
    async def play(self, ctx: commands.Context, *, query: str):
        """Play or add song to queue (Defaults to YouTube)"""
        if not ctx.voice_client:
                player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
                self.bot.dispatch("nextmusic_player_connect", player)
                await ctx.send('Node connecting...', delete_after=1)

        player: wavelink.Player = ctx.voice_client
        player.bound_channel = ctx.channel
        player.bot = self.bot
        await self.play_track(ctx, query)

    @play.command(aliases=["yt"])
    @voice_connected()
    async def youtube(self, ctx: commands.Context, *, query: str):
        """Play a YouTube track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "yt")

    @play.command(aliases=["ytmusic"])
    @voice_connected()
    async def youtubemusic(self, ctx: commands.Context, *, query: str):
        """Play a YouTubeMusic track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "ytmusic")

    @play.command(aliases=["sc"])
    @voice_connected()
    async def soundcloud(self, ctx: commands.Context, *, query: str):
        """Play a SoundCloud track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "soundcloud")

    @play.command(aliases=["sp"])
    @voice_connected()
    async def spotify(self, ctx: commands.Context, *, query: str):
        """play a spotify track"""
        await ctx.invoke(self.connect)
        await self.play_track(ctx, query, "spotify")

    @commands.command(aliases=["vol"])
    @voice_channel_player()
    async def volume(self, ctx: commands.Context, vol: int, forced=False):
        """Set volume"""
        player: NextPlayer = ctx.voice_client

        if vol < 0:
            return await ctx.send("Volume can't be less than 0")

        if vol > 100 and not forced:
            return await ctx.send("Volume can't greater than 100")

        await player.set_volume(vol)
        await ctx.send(f"Volume set to {vol} :loud_sound:")

    @commands.command(aliases=["disconnect", "dc"])
    @voice_channel_player()
    async def stop(self, ctx: commands.Context):
        """Stop the player"""
        player: NextPlayer = ctx.voice_client

        await player.destroy()
        await ctx.send("Stopped the player :stop_button: ")
        self.bot.dispatch("nextmusic_player_stop", player)

    @commands.command()
    @voice_channel_player()
    async def pause(self, ctx: commands.Context):
        """Pause the player"""
        player: NextPlayer = ctx.voice_client

        if player.is_playing():
            if player.is_paused():
                return await ctx.send("Player is already paused.")

            await player.set_pause(pause=True)
            self.bot.dispatch("nextmusic_player_pause", player)
            return await ctx.send("Paused :pause_button: ")

        await ctx.send("Player is not playing anything.")

    @commands.command()
    @voice_channel_player()
    async def resume(self, ctx: commands.Context):
        """Resume the player"""
        player: NextPlayer = ctx.voice_client

        if player.is_playing():
            if not player.is_paused():
                return await ctx.send("Player is already playing.")

            await player.set_pause(pause=False)
            self.bot.dispatch("nextmusic_player_resume", player)
            return await ctx.send("Resumed :musical_note: ")

        await ctx.send("Player is not playing anything.")

    @commands.command()
    @voice_channel_player()
    async def skip(self, ctx: commands.Context):
        """Skip to next song in the queue."""
        player: NextPlayer = ctx.voice_client

        if player.loop == "CURRENT":
            player.loop = "NONE"

        await player.stop()

        self.bot.dispatch("nextmusic_track_skip", player)
        await ctx.send("Skipped :track_next:")

    @commands.command()
    @voice_channel_player()
    async def seek(self, ctx: commands.Context, seconds: int):
        """Seek the player backward or forward"""
        player: NextPlayer = ctx.voice_client

        if player.is_playing():
            old_position = player.position
            position = old_position + seconds
            if position > player.source.length:
                return await ctx.send("Can't seek past the end of the track.")

            if position < 0:
                position = 0

            await player.seek(position * 1000)
            self.bot.dispatch("nextmusic_player_seek", player, old_position, position)
            return await ctx.send(f"Seeked {seconds} seconds :fast_forward: ")

        await ctx.send("Player is not playing anything.")

    @commands.command()
    @voice_channel_player()
    async def loop(self, ctx: commands.Context, loop_type: str = None):
        """Set loop to `NONE`, `CURRENT` or `PLAYLIST`"""
        player: NextPlayer = ctx.voice_client

        result = await player.set_loop(loop_type)
        await ctx.send(f"Loop has been set to {result} :repeat: ")

    @commands.command(aliases=["q"])
    @voice_channel_player()
    async def queue(self, ctx: commands.Context):
        """Player queue"""
        player: NextPlayer = ctx.voice_client

        if len(player.queue._queue) < 1:
            return await ctx.send("Nothing is in the queue.")

        paginator = Paginator(ctx, player)
        await paginator.start()

    @commands.command(aliases=["np"])
    @voice_channel_player()
    async def nowplaying(self, ctx: commands.Context):
        """Currently playing song information"""
        player: NextPlayer = ctx.voice_client
        await player.invoke_player(ctx)


    @commands.group(aliases=["24/7", "247", "24"], invoke_without_command=True)
    async def tofourseven(self, ctx):
        if self.cluster == None:
            await ctx.send(embed=self.musicEmb('24/7 Mode', 'You can\'t use 24/7 mode because the bot owner isn\'t added mongo url.'))
        else:
            await ctx.send(embed=self.musicEmb('24/7 Mode', 'To enable 24/7 mode use ```247 enable```\nTo disable 24/7 mode use ```247 disable```'))



    @tofourseven.command(name='enable', aliases=['e'])
    @voice_connected()
    async def tofourseven_enable(self, ctx):
        if self.cluster == None:
            await ctx.send(embed=self.musicEmb('24/7 Mode', 'You can\'t use 24/7 mode because the bot owner isn\'t added mongo url.'))

        else:
            find = await self._247.find_one({"guild": ctx.guild.id})
            if find is None:
                await self._247.insert_one({"guild": ctx.guild.id, "vcid": ctx.author.voice.channel.id})
                await ctx.send(embed=self.musicEmb('24/7 Mode', f'24/7 mode is enabled in <#{ctx.author.voice.channel.id}>'))
            else:
                await ctx.send(embed=self.musicEmb('24/7 Mode', '24/7 mode is already enabled.'))


    @tofourseven.command(name='disable', aliases=['d'])
    async def tofourseven_disable(self, ctx):
        if self.cluster == None:
            await ctx.send(embed=self.musicEmb('24/7 Mode', 'You can\'t use 24/7 mode because the bot owner isn\'t added mongo url.'))


        else:
            find = await self._247.find_one({"guild": ctx.guild.id})
            if find:
                await self._247.delete_one({"guild": ctx.guild.id})
                await ctx.send(embed=self.musicEmb('24/7 Mode', '24/7 mode is disabled now.'))

            else:
                await ctx.send(embed=self.musicEmb('24/7 Mode', '24/7 is not enabled.'))

