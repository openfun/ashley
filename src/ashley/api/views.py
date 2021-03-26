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
from rest_framework.response import Response

from ashley.context_mixins import get_current_lti_session
from ashley.defaults import (
    _FORUM_ROLE_INSTRUCTOR,
    _FORUM_ROLE_MODERATOR,
    _FORUM_ROLE_STUDENT,
)
from ashley.permissions import ManageModeratorPermission

from .serializers import UserSerializer

User = get_user_model()
LTIContext = get_model("ashley", "LTIContext")
Forum = get_model("forum", "Forum")
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
        role = self.request.GET.get("role", False)

        # Filter all the users that are moderators or students."""
        if role == _FORUM_ROLE_STUDENT:
            # Gets all the students for the current LTIContext.
            return (
                User.objects.filter(
                    is_active=True,
                    groups__name=context.get_group_role_name(_FORUM_ROLE_STUDENT),
                )
                .exclude(
                    groups__name=context.get_group_role_name(_FORUM_ROLE_MODERATOR)
                )
                .order_by(self.ordering)
            )
        if role == _FORUM_ROLE_MODERATOR:
            # Gets all the moderators for the current LTIContext.Moderators have
            # the primitive role student."""
            return (
                User.objects.filter(
                    is_active=True,
                    groups__name=context.get_group_role_name(_FORUM_ROLE_MODERATOR),
                )
                .filter(groups__name=context.get_group_role_name(_FORUM_ROLE_STUDENT))
                .order_by(self.ordering)
            )
        if role == _FORUM_ROLE_INSTRUCTOR:
            # Gets all the instructor for the current LTIContext.
            return User.objects.filter(
                is_active=True,
                groups__name=context.get_group_role_name(_FORUM_ROLE_INSTRUCTOR),
            ).order_by(self.ordering)

        # If no role is specified, filter all the users for the current LTIContext
        return (
            User.objects.filter(
                groups__name__startswith=context.get_group_role_name("")
            )
            .order_by(self.ordering)
            .distinct()
        )

    # pylint: disable=W0221
    def update(self, request, pk=None):
        """Update method is used to promote or revoke moderator role on student users"""
        user = User.objects.get(pk=pk)
        context = get_current_lti_session(self.request)
        # Collect group name informations
        group_moderator_name = context.get_group_role_name(_FORUM_ROLE_MODERATOR)
        group_student_name = context.get_group_role_name(_FORUM_ROLE_STUDENT)
        group_moderator = context.get_role_group(_FORUM_ROLE_MODERATOR)
        # Load current groups
        user_groups = list(user.groups.values_list("name", flat=True))

        # Role asked is student, check user is both student and moderator before removing the group
        if (
            self.request.data.get("role") == _FORUM_ROLE_STUDENT
            and group_moderator_name in user_groups
            and group_student_name in user_groups
        ):
            user.groups.remove(group_moderator)
            user.save()
        # Role asked is moderator, check user is student and not yet moderator before adding
        # the group moderator
        elif (
            self.request.data.get("role") == _FORUM_ROLE_MODERATOR
            and group_student_name in user_groups
            and group_moderator_name not in user_groups
        ):
            user.groups.add(group_moderator)
            user.save()
        else:
            logger.debug(
                "Update moderator forbidden - Role asked %s - user groups %s",
                self.request.data.get("role"),
                user_groups,
            )
            raise PermissionDenied()

        return Response({"success": True}, status=status.HTTP_200_OK)
