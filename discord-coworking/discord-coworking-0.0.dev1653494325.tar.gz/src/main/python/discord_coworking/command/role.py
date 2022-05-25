from dataclasses import dataclass
from dataclasses import field
from typing import Optional

from discord import Client as DiscordClient
from discord import Guild, Role, Color, Permissions

from discord_coworking.command.api import Result
from discord_coworking.command.api import UnundoableResult
from discord_coworking.command.guild import GuildResult, GuildCommand, GuildPredicate
from discord_coworking.command.predicate import ByAttributesPredicate
from discord_coworking.command.predicate import Predicate, ANY


class RolePredicate(ByAttributesPredicate[Role]):

    @classmethod
    def of(cls, role: Role):
        return cls.create(id=role.id)


class DefaultRolePredicate(Predicate[Role]):

    def __call__(self, e: Role) -> bool:
        return e.is_default()


class AdminRolePredicate(Predicate[Role]):

    def __call__(self, e: Role) -> bool:
        return e.permissions.administrator


DEFAULT_ROLE = DefaultRolePredicate()
NOT_DEFAULT_ROLE = -DEFAULT_ROLE
MANAGED_ROLE = RolePredicate.create(managed=True)
NOT_MANAGED_ROLE = -MANAGED_ROLE
ADMIN_ROLE = AdminRolePredicate()
NOT_ADMIN_ROLE = -ADMIN_ROLE


@dataclass()
class RoleCreated(GuildResult):
    role: Predicate[Role] = ANY

    @classmethod
    def create(cls, guild: Guild, role: Role):
        return cls(
            guild=GuildPredicate.of(guild),
            role=RolePredicate.of(role),
        )

    async def undo_on_guild(self, client: DiscordClient, guild: Guild):
        for role in filter(self.role, guild.roles):
            await role.delete()


@dataclass()
class CreateRole(GuildCommand):
    name: str = None
    permissions: Permissions = field(default_factory=Permissions.none)
    color: Color = field(default_factory=Color.default)
    hoist: bool = False
    mentionable: bool = False
    reason: Optional[str] = None

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> RoleCreated:
        role = await guild.create_role(
            name=self.name,
            permissions=self.permissions,
            colour=self.color,
            hoist=self.hoist,
            mentionable=self.mentionable,
            reason=self.reason,
        )
        return RoleCreated.create(guild, role)


@dataclass()
class DeleteRole(GuildCommand):
    role: RolePredicate = NOT_DEFAULT_ROLE & NOT_MANAGED_ROLE & NOT_ADMIN_ROLE

    async def do_on_guild(self, client: DiscordClient, guild: Guild) -> Result:
        for role in self.role.filter(guild.roles):
            await role.delete()
        return UnundoableResult.create(self)
