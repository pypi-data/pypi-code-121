from dataclasses import dataclass
from typing import Dict
from typing import Optional

from discord import Client as DiscordClient
from discord import Guild, VoiceChannel, CategoryChannel
from discord import Role, PermissionOverwrite

from discord_coworking.command.api import Result, UnundoableResult
from discord_coworking.command.guild import GuildResult, GuildCommand, GuildPredicate
from discord_coworking.command.overwrites import OverwritesMixin
from discord_coworking.command.predicate import ANY, NONE
from discord_coworking.command.predicate import ByAttributesPredicate, Predicate


class VoiceChannelPredicate(ByAttributesPredicate[VoiceChannel]):

    @classmethod
    def of(cls, voice_channel: VoiceChannel):
        return cls.create(id=voice_channel.id)


@dataclass()
class VoiceChannelCreated(GuildResult):
    voice_channel: Predicate[VoiceChannel] = ANY

    @classmethod
    def create(cls, guild: Guild, voice_channel: VoiceChannel):
        return cls(
            guild=GuildPredicate.of(guild),
            voice_channel=VoiceChannelPredicate.of(voice_channel),
        )

    async def undo_on_guild(self, client: DiscordClient, guild: Guild):
        for voice_channel in self.voice_channel.filter(guild.voice_channels):
            await voice_channel.delete()


@dataclass()
class CreateVoiceChannel(GuildCommand, OverwritesMixin):
    name: str = None
    bitrate: Optional[int] = None
    user_limit: Optional[int] = None
    category: Predicate[CategoryChannel] = NONE
    overwrites: Optional[Dict[Predicate[Role], PermissionOverwrite]] = None

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> VoiceChannelCreated:
        voice_channel = await guild.create_voice_channel(
            name=self.name,
            bitrate=self.bitrate,
            user_limit=self.user_limit,
            category=self.category.any(guild.categories),
            overwrites=self.get_overwrites(guild),
        )
        return VoiceChannelCreated.create(guild, voice_channel)


class DeleteVoiceChannel(GuildCommand):
    voice_channel: Predicate[VoiceChannel] = ANY

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> Result:
        for voice_channel in self.voice_channel.filter(guild.voice_channels):
            await voice_channel.delete()
        return UnundoableResult.create(self)
