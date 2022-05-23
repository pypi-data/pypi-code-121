import typing as ty

if ty.TYPE_CHECKING:
   from .context import GuildMessageCtx, AuthorAwareCtx, CommandCtx
   from auth import AuthAwareCtx
   from .flux import FluxEvent, FluxClient

   ExtraCtxs: ty.TypeAlias = ty.Literal["auth"]


   # noinspection PyUnresolvedReferences
   class GuildCommandCtx(CommandCtx):
      flux: FluxClient
      msg_ctx: GuildMessageCtx
      author_ctx: AuthorAwareCtx
      auth_ctxs: ty.List[AuthAwareCtx]


   class GuildCommandEvent(FluxEvent):
      flux: FluxClient
      cmd_name: str
      cmd_ctx: GuildCommandCtx
      cmd_args: ty.Optional[str]


   class CommandFunc(ty.Protocol):
      __name__: str

      def __call__(self, ctx: CommandCtx, cmd_args: str = None, cmd_flags:ty.List[str] = None, **kwargs): ...
