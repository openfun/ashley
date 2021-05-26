"""Views of the ashley api django application."""
import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ashley.context_mixins import get_current_lti_session
from ashley.defaults import _FORUM_ROLE_INSTRUCTOR, _FORUM_ROLE_MODERATOR
from ashley.permissions import ManageModeratorPermission

from .serializers import UploadImageSerializer, UserSerializer

User = get_user_model()
LTIContext = get_model("ashley", "LTIContext")
Forum = get_model("forum", "Forum")
UploadImage = get_model("ashley", "UploadImage")
PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)
logger = logging.getLogger(__name__)


class UserApiView(
    mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):  # pylint: disable=too-many-ancestors
    """API requests to list moderators for current LTIContext"""

    # Add permission to check if user has the right permission and can manage moderators
    permission_classes = [ManageModeratorPermission]
    serializer_class = UserSerializer
    ordering = "public_username"

    def get_queryset(self):
        context = get_current_lti_session(self.request)
        role = self.request.GET.get("role", None)
        # Select all active users who are part of the current LTIContext
        query = User.objects.filter(
            is_active=True,
            groups__name=context.base_group_name,
        )
        # If a role is specified and start with !, we exclude its members from the results
        if role is not None and role.startswith("!"):
            query = query.exclude(groups__name=context.get_group_role_name(role[1:]))
        # If a role is specified, we select only users having this role inside the LTIContext
        elif role:
            query = query.filter(groups__name=context.get_group_role_name(role))
        # When the role moderator (or !moderator) is specified, we want to exclude the
        # users having the instructor role from the results.
        if role in [_FORUM_ROLE_MODERATOR, f"!{_FORUM_ROLE_MODERATOR}"]:
            query = query.exclude(
                groups__name=context.get_group_role_name(_FORUM_ROLE_INSTRUCTOR)
            )
        return query.order_by(self.ordering)

    # pylint: disable=W0221
    def update(self, request, pk=None):
        """Update method is used to promote or revoke moderator role"""
        user = User.objects.get(pk=pk)
        lti_context = get_current_lti_session(self.request)
        roles = self.request.data.get("roles", [])
        # Load current groups
        user_groups = lti_context.get_user_roles(user)
        group_moderator = lti_context.get_role_group(_FORUM_ROLE_MODERATOR)

        # Asked to revoke moderator,
        if _FORUM_ROLE_MODERATOR not in roles and _FORUM_ROLE_MODERATOR in user_groups:
            user.groups.remove(group_moderator)
            user.save()
        # Asked to become moderator, check user is not yet moderator and make sure user
        # belongs to this context by checking he has groups from this context.
        elif (
            _FORUM_ROLE_MODERATOR in roles
            and _FORUM_ROLE_MODERATOR not in user_groups
            and len(user_groups) > 0
        ):
            user.groups.add(group_moderator)
            user.save()
        else:
            logger.debug(
                "Update moderator forbidden - Role asked %s - user groups %s",
                roles,
                user_groups,
            )
            raise PermissionDenied()

        return Response({"success": True}, status=status.HTTP_200_OK)


# pylint: disable=too-many-ancestors
class ImageUploadApiView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Viewset for the API of the Image object."""

    queryset = UploadImage.objects.all()
    serializer_class = UploadImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Preset poster field with current user"""
        serializer.save(poster=self.request.user)
