"""This application overrides to django-machina's forum_conversation app."""

# pylint: disable=invalid-name
default_app_config = (
    "ashley.machina_extensions.forum_conversation.apps.ForumConversationAppConfig"
)
