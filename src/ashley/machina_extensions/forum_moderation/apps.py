"""Ashley application"""
from machina.apps.forum_moderation.apps import (
    ForumModerationAppConfig as BaseForumModerationAppConfig,
)


class ForumModerationAppConfig(BaseForumModerationAppConfig):
    """Configuration class for the forum_conversation app."""

    name = "ashley.machina_extensions.forum_moderation"
