from __future__ import annotations

import typing as ty
import dataclasses as dtcs
import abc
import itertools as itt
import discord
from loguru import logger

if ty.TYPE_CHECKING:
   from .context import AuthAwareCtx
   from .command import Command


@dtcs.dataclass
class AuthList:
   user: ty.Optional[int] = None
   roles: ty.List[int] = dtcs.field(default_factory=list)
   permissions: ty.Optional[discord.Permissions] = None


@dtcs.dataclass(frozen=True)
class Record:
   # topic : str
   rule: ty.Literal["ALLOW", "DENY"]
   target_id: int
   target_type: ty.Literal["MEMBER", "ROLE", "PERMISSION", "ALL"]

   def __post_init__(self):
      if self.rule not in ["ALLOW", "DENY"]:
         raise TypeError(
            f"Attempted to create a record with a RULE not in ['ALLOW','DENY']: {self}")
      if self.target_type not in ["MEMBER", "ROLE", "PERMISSION", "ALL"]:
         raise TypeError(
            f"Attempted to create a record with a TARGET_TYPE not in ['MEMBER', 'ROLE', 'PERMISSION', 'ALL']")

   def to_dict(self):
      return dtcs.asdict(self)

   @classmethod
   def admin_record(cls, admin_id: int):
      return cls(rule="ALLOW", target_id=admin_id, target_type="MEMBER")

   @classmethod
   def allow_perm(cls, perm: discord.Permissions):
      return cls(rule="ALLOW", target_id=perm.value, target_type="PERMISSION")

   @classmethod
   def allow_server_manager(cls):
      return cls(rule="ALLOW", target_id=discord.Permissions(manage_guild=True).value, target_type="PERMISSION")

   @classmethod
   def deny_all(cls):
      return cls(rule="DENY", target_id=0, target_type="ALL")

   @classmethod
   def allow_all(cls):
      return cls(rule="ALLOW", target_id=0, target_type="ALL")

   def evaluate(self, auth_list: AuthList) -> ty.Optional[bool]:
      if (
            (self.target_type == "ALL") or
            (self.target_type == "PERMISSION" and auth_list.permissions and discord.Permissions(permissions=self.target_id) <= auth_list.permissions) or
            (self.target_type == "ROLE" and self.target_id in auth_list.roles) or
            (self.target_type == "MEMBER" and self.target_id == auth_list.user)
      ):
         return self.rule == "ALLOW"
      return None

   PRECEDENCE = {
      "MEMBER"    : 0,
      "ROLE"      : -1,
      "PERMISSION": -2,
      "ALL"       : -3
   }


class AuthAware:
   @property
   @abc.abstractmethod
   def default_auths(self) -> ty.List[Record]: ...

   @property
   @abc.abstractmethod
   def override_auths(self) -> ty.List[Record]: ...

   @property
   @abc.abstractmethod
   def auth_id(self) -> str: ...


class Auth:

   @staticmethod
   def order_records(records: ty.List[Record]):
      return sorted(records, key=lambda record: Record.PRECEDENCE[record.target_type])

   @staticmethod
   def accepts(ctx: AuthAwareCtx, cmd: Command):
      auths = ctx.config["auths"]
      logger.trace(f"Evaluating authentication for {cmd}")

      cog_defaults = Auth.order_records(cmd.cog.default_auths)
      cmd_defaults = Auth.order_records(cmd.default_auths)

      cog_specifics = Auth.order_records(
         [Record(**record) for record in (auths.get(cmd.cog.auth_id, []))])
      cmd_specifics = Auth.order_records(
         [Record(**record) for record in (auths.get(cmd.auth_id, []))])

      cog_overrides = Auth.order_records(cmd.cog.override_auths)
      cmd_overrides = Auth.order_records(cmd.override_auths)

      accepts = False  # True if the last applicable record is True
      for record in itt.chain(cog_defaults, cmd_defaults, cog_specifics, cmd_specifics, cog_overrides, cmd_overrides, [Record.admin_record(ctx.config["admin_id"])]):
         logger.trace(f"Evaluating {record}")
         res = record.evaluate(ctx.auth_list)
         logger.trace(f"Result: {res}")
         if res is not None:
            accepts = res

      return accepts

   @staticmethod
   def accepts_all(ctxs: ty.List[AuthAwareCtx], cmd: Command):
      return all(Auth.accepts(ctx, cmd) for ctx in ctxs)

   @staticmethod
   async def add_record(ctx: AuthAwareCtx, auth_id: str, record: Record):
      async with ctx.flux.CONFIG.writeable_conf(ctx) as cfg_w:
         if auth_id in cfg_w["auths"]:
            cfg_w["auths"][auth_id] = [auth_rec for auth_rec in cfg_w["auths"]
            [auth_id] if auth_rec["target_id"] != record.target_id]
            cfg_w["auths"][auth_id].append(record.to_dict())
         else:
            cfg_w["auths"][auth_id] = [record.to_dict()]
