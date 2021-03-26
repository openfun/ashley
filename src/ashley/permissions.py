"""Custom permission classes for the Ashley project."""
from django.core.exceptions import PermissionDenied
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.loading import get_class

from ashley.context_mixins import get_current_lti_session_first_forum

PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)


class ManageModeratorPermission(PermissionRequiredMixin):
    """
    Permission based on LTIContext Session.
    Class used by API and view on managing moderators for current session LTIContext.
    """

    @classmethod
    def _get_forum(cls, request):
        """LTIContext can have multiple forum, we target the first one"""
        try:
            return get_current_lti_session_first_forum(request)
        except Exception as no_forum:
            raise PermissionDenied() from no_forum

    @classmethod
    def _can(cls, request):
        """Check user has permission `can_manage_moderator` for first forum in this LTIContext"""
        return request.forum_permission_handler.can_manage_moderator(
            ManageModeratorPermission._get_forum(request), request.user
        )

    # pylint: disable=unused-argument
    def has_permission(self, request, view):
        """Check user has permission `can_manage_moderator` for first forum in this LTIContext"""
        return self._can(request)

    # pylint: disable=unused-argument
    def perform_permissions_check(self, user, obj, perms):
        """Check user has permission `can_manage_moderator` for first forum in this LTIContext"""
        return self._can(self.request)

    def has_object_permission(self, request, view, obj):
        """Check user has permission `can_manage_moderator` for first forum in this LTIContext"""
        return self._can(request)
