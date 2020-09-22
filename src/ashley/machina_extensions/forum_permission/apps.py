"""Ashley forum_permission application"""
from machina.apps.forum_permission.apps import (
    ForumPermissionAppConfig as BaseForumPermissionAppConfig,
)


class ForumPermissionAppConfig(BaseForumPermissionAppConfig):
    """Configuration class for the forum_permission app."""

    name = "ashley.machina_extensions.forum_permission"
