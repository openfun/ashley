"""This application overrides django-machina's forum_moderation app."""

# pylint: disable=invalid-name
default_app_config = (
    "ashley.machina_extensions.forum_moderation.apps.ForumModerationAppConfig"
)
