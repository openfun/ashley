"""
This module defines a ``PermissionHandler`` abstraction that allows to
implement filter or access logic related to forums.
"""
from typing import Optional

from machina.apps.forum_permission.handler import (
    PermissionHandler as BasePermissionHandler,
)


class PermissionHandler(BasePermissionHandler):
    """Add ashley specific permission checks to the machina permission handler."""

    def __init__(self):
        """Constructor"""
        super().__init__()
        # This attribute is used to store the LTIContext of the current user.
        # (see middleware.ForumPermission)
        # It allows the permission checking functions to be aware of the current LTIContext
        # we are scoped into, if any.
        self.current_lti_context_id: Optional[int] = None

    def can_rename_forum(self, forum, user):
        """ Given a forum, checks whether the user can rename it. """
        return self._perform_basic_permission_check(forum, user, "can_rename_forum")

    def forum_list_filter(self, qs, user):
        """
        Filters the given queryset in order to return a list of forums that
        can be seen and read by the specified user (at least).

        We override django machina's method to filter forums based on the
        current LTI context of the User, if any.
        """
        forums_to_show = super().forum_list_filter(qs, user)
        if self.current_lti_context_id:
            return forums_to_show.filter(lti_contexts__id=self.current_lti_context_id)
        return forums_to_show
