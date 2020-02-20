"""lti_provider application."""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LtiProviderAppConfig(AppConfig):
    """Configuration class for the lti_provider app."""

    verbose_name = _("LTI Provider")
    name = "lti_provider"
