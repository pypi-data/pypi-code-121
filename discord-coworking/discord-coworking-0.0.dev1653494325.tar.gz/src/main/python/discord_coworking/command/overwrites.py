from typing import Optional, Dict

from discord import Role, PermissionOverwrite, Guild

from discord_coworking.command.predicate import Predicate


class OverwritesMixin:
    overwrites: Optional[Dict[Predicate[Role], PermissionOverwrite]] = None

    def get_overwrites(self, guild: Guild) -> Optional[Dict[Role, PermissionOverwrite]]:
        if self.overwrites is None:
            return None
        return dict(
            (role_id.any(guild.roles), perms)
            for role_id, perms in self.overwrites.items()
        )
