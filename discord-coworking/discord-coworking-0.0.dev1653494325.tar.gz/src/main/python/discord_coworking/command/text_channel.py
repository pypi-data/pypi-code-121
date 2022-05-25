from dataclasses import dataclass
from typing import Optional, Dict

from discord import Client as DiscordClient
from discord import Guild, TextChannel, CategoryChannel, Role, PermissionOverwrite

from discord_coworking.command.api import Result, UnundoableResult
from discord_coworking.command.guild import GuildResult, GuildCommand, GuildPredicate
from discord_coworking.command.overwrites import OverwritesMixin
from discord_coworking.command.predicate import ANY, NONE
from discord_coworking.command.predicate import ByAttributesPredicate, Predicate


class TextChannelPredicate(ByAttributesPredicate[TextChannel]):

    @classmethod
    def of(cls, text_channel: TextChannel):
        return cls.create(id=text_channel.id)


@dataclass()
class TextChannelCreated(GuildResult):
    text_channel: Predicate[TextChannel] = ANY

    @classmethod
    def create(cls, guild: Guild, text_channel: TextChannel):
        return cls(
            guild=GuildPredicate.of(guild),
            text_channel=TextChannelPredicate.of(text_channel),
        )

    async def undo_on_guild(self, client: DiscordClient, guild: Guild):
        for text_channel in self.text_channel.filter(guild.text_channels):
            await text_channel.delete()


@dataclass()
class CreateTextChannel(GuildCommand, OverwritesMixin):
    name: str = None
    topic: Optional[str] = None
    category: Predicate[CategoryChannel] = NONE
    overwrites: Optional[Dict[Predicate[Role], PermissionOverwrite]] = None

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> TextChannelCreated:
        text_channel = await guild.create_text_channel(
            name=self.name,
            topic=self.topic,
            category=self.category.any(guild.categories),
            overwrites=self.get_overwrites(guild),
        )
        return TextChannelCreated.create(guild, text_channel)


class DeleteTextChannel(GuildCommand):
    text_channel: Predicate[TextChannel] = ANY

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> Result:
        for text_channel in self.text_channel.filter(guild.text_channels):
            await text_channel.delete()
        return UnundoableResult.create(self)
