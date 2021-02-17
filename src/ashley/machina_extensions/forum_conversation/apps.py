"""Ashley application"""
from machina.apps.forum_conversation.apps import (
    ForumConversationAppConfig as BaseForumConversationAppConfig,
)


class ForumConversationAppConfig(BaseForumConversationAppConfig):
    """Configuration class for the forum_conversation app."""

    name = "ashley.machina_extensions.forum_conversation"
