"""
This module defines the default permissions that can be configured for a forum
application.
"""

from django.utils.translation import gettext_lazy as _
from machina.apps.forum_permission.defaults import (
    PermissionConfig as BasePermissionConfig,
)


class PermissionConfig(BasePermissionConfig):
    """
    Overrides the PermissionConfig class from machina forum_permission
    application to add custom permissions.
    """

    permissions = BasePermissionConfig.permissions + [
        # Forums
        {
            "codename": "can_archive_forum",
            "label": _("Can archive a forum"),
            "scope": "forum",
        },
        {
            "codename": "can_rename_forum",
            "label": _("Can rename a forum"),
            "scope": "forum",
        },
        {
            "codename": "can_manage_moderator",
            "label": _("Can manage a user's moderator status"),
            "scope": "forum",
        },
    ]
