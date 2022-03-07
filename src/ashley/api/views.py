"""Views of the ashley api django application."""
import logging

from django.contrib.auth import get_user_model
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ashley.context_mixins import get_current_lti_session
from ashley.defaults import (
    _FORUM_ROLE_INSTRUCTOR,
    _FORUM_ROLE_MODERATOR,
    _FORUM_ROLE_STUDENT,
)
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

    @action(detail=True, methods=["patch"])
    # pylint: disable=invalid-name, unused-argument
    def remove_group_moderator(
        self,
        request,
        pk=None,
    ):
        """Remove group moderator."""
        user = self.get_object()
        lti_context = get_current_lti_session(self.request)
        # Asked to revoke moderator,
        if _FORUM_ROLE_MODERATOR in lti_context.get_user_roles(user):
            user.groups.remove(lti_context.get_role_group(_FORUM_ROLE_MODERATOR))

        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=["patch"])
    # pylint: disable=invalid-name, unused-argument
    def add_group_moderator(
        self,
        request,
        pk=None,
    ):

        """Add group moderator."""
        user = self.get_object()

        lti_context = get_current_lti_session(self.request)

        # Load current groups
        user_groups = lti_context.get_user_roles(user)
        # Asked to become moderator, check user is not yet moderator and make sure user
        # belongs to this context by checking he has the group student from this context.
        if (
            _FORUM_ROLE_MODERATOR not in user_groups
            and _FORUM_ROLE_STUDENT in user_groups
        ):
            user.groups.add(lti_context.get_role_group(_FORUM_ROLE_MODERATOR))

        return Response(self.get_serializer(user).data)


# pylint: disable=too-many-ancestors
class ImageUploadApiView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Viewset for the API of the Image object."""

    queryset = UploadImage.objects.all()
    serializer_class = UploadImageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Preset poster field with current user"""
        serializer.save(poster=self.request.user)
