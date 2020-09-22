"""
This module defines a ``PermissionHandler`` abstraction that allows to
implement filter or access logic related to forums.
"""

from machina.apps.forum_permission.handler import (
    PermissionHandler as BasePermissionHandler,
)


class PermissionHandler(BasePermissionHandler):
    """Add ashley specific permission checks to the machina permission handler."""

    def can_rename_forum(self, forum, user):
        """ Given a forum, checks whether the user can rename it. """
        return self._perform_basic_permission_check(forum, user, "can_rename_forum")
