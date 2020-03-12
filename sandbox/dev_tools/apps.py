"""dev_tools application config."""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DevToolsAppConfig(AppConfig):
    """Configuration class for the dev_tools app."""

    verbose_name = _("Dev tools")
    name = "dev_tools"
