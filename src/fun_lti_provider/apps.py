"""Ashley application"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FunLtiProviderAppConfig(AppConfig):
    """Configuration class for the fun_lti_provider app."""

    verbose_name = _("FUN:LTI Provider")
    name = "fun_lti_provider"
