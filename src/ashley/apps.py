"""Ashley application"""
from django.apps import AppConfig


class AshleyConfig(AppConfig):
    """Configuration class for the ashley app."""

    name = "ashley"

    def ready(self):
        """ Executes whatever is necessary when the application is ready. """
        # pylint: disable=import-outside-toplevel,unused-import
        from . import receivers  # noqa: F401
