"""Ashley application"""
from machina.apps.forum.apps import ForumAppConfig as BaseForumAppConfig


class ForumAppConfig(BaseForumAppConfig):
    """Configuration class for the forum app."""

    name = "ashley.machina_extensions.forum"
