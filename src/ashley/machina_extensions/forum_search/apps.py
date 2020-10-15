"""Ashley application"""
from machina.apps.forum_search.apps import (
    ForumSearchAppConfig as BaseForumSearchAppConfig,
)


class ForumSearchAppConfig(BaseForumSearchAppConfig):
    """Configuration class for the forum_search app."""

    name = "ashley.machina_extensions.forum_search"
