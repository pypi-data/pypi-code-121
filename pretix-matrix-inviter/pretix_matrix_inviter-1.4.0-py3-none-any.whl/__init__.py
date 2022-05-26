from django.utils.translation import gettext_lazy

try:
    from pretix.base.plugins import PluginConfig
except ImportError:
    raise RuntimeError("Please use pretix 2.7 or above to run this plugin!")

__version__ = "1.4.0"


class PluginApp(PluginConfig):
    name = "pretix_matrix_inviter"
    verbose_name = "Matrix inviter"

    class PretixPluginMeta:
        name = gettext_lazy("Matrix inviter")
        author = "Felix Schäfer"
        description = gettext_lazy(
            "Invite Pretix participants to a Matrix Room or Space."
        )
        visible = True
        version = __version__
        category = "FEATURE"
        compatibility = "pretix>=2.7.0"

    def ready(self):
        from . import signals  # NOQA


default_app_config = "pretix_matrix_inviter.PluginApp"
