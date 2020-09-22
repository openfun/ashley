"""This application overrides django-machina's forum_permission app."""

# pylint: disable=invalid-name
default_app_config = (
    "ashley.machina_extensions.forum_permission.apps.ForumPermissionAppConfig"
)
