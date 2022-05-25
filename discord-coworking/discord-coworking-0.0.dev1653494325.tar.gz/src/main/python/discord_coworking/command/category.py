from dataclasses import dataclass
from typing import Optional, Dict

from discord import Client as DiscordClient
from discord import Guild, CategoryChannel
from discord import Role, PermissionOverwrite

from discord_coworking.command.api import Result, UnundoableResult
from discord_coworking.command.guild import GuildResult, GuildCommand, GuildPredicate
from discord_coworking.command.overwrites import OverwritesMixin
from discord_coworking.command.predicate import ByAttributesPredicate
from discord_coworking.command.predicate import Predicate, ANY


class CategoryPredicate(ByAttributesPredicate[CategoryChannel]):

    @classmethod
    def of(cls, category: CategoryChannel):
        return cls.create(id=category.id)


@dataclass()
class CategoryCreated(GuildResult):
    category: Predicate[CategoryChannel] = ANY

    @classmethod
    def create(cls, guild: Guild, category: CategoryChannel):
        return cls(
            guild=GuildPredicate.of(guild),
            category=CategoryPredicate.of(category),
        )

    async def undo_on_guild(self, client: DiscordClient, guild: Guild):
        for category in self.category.filter(guild.categories):
            await category.delete()


@dataclass()
class CreateCategory(GuildCommand, OverwritesMixin):
    name: str = None
    overwrites: Optional[Dict[Predicate[Role], PermissionOverwrite]] = None

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> CategoryCreated:
        category = await guild.create_category(
            name=self.name,
            overwrites=self.get_overwrites(guild),
        )
        return CategoryCreated.create(guild, category)


class DeleteCategory(GuildCommand):
    category: Predicate[CategoryChannel] = ANY

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> Result:
        for category in self.category.filter(guild.categories):
            await category.delete()
        return UnundoableResult.create(self)
