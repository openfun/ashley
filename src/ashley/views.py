"""Views of the ashley django application."""
import logging
from typing import List

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView
from lti_toolbox.lti import LTI
from lti_toolbox.views import BaseLTIAuthView
from machina.apps.forum_permission.shortcuts import assign_perm, remove_perm
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

from ashley.permissions import ManageModeratorPermission

from . import SESSION_LTI_CONTEXT_ID
from .defaults import (
    DEFAULT_FORUM_BASE_PERMISSIONS,
    DEFAULT_FORUM_BASE_READ_PERMISSIONS,
    DEFAULT_FORUM_BASE_WRITE_PERMISSIONS,
    DEFAULT_FORUM_ROLES_PERMISSIONS,
)

GroupForumPermission = get_model("forum_permission", "GroupForumPermission")
Forum = get_model("forum", "Forum")  # pylint: disable=C0103
LTIContext = get_model("ashley", "LTIContext")  # pylint: disable=C0103
PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)
User = get_user_model()

logger = logging.getLogger(__name__)


class ForumLTIView(BaseLTIAuthView):
    """Forum view called by an LTI launch request."""

    def _do_on_login(self, lti_request: LTI) -> HttpResponse:
        """Process the request when the user is logged in via LTI"""

        # Get or create the LTIContext model associated with the current LTI launch request
        context_id = lti_request.get_param("context_id")
        if not context_id:
            return HttpResponseBadRequest("LTI parameter context_id is mandatory")
        context, _context_created = LTIContext.objects.get_or_create(
            lti_id=context_id, lti_consumer=lti_request.get_consumer()
        )

        # Synchronize the user groups related to the current LTI context
        context.sync_user_groups(self.request.user, lti_request.roles)

        # Store the current user LTI context in session
        self.request.session[SESSION_LTI_CONTEXT_ID] = context.id

        # Get or create the requested forum
        forum_uuid = self.kwargs["uuid"]
        # The requested forum must exist in this context or needs to be created
        try:
            forum = Forum.objects.get(
                lti_id=forum_uuid,
                type=Forum.FORUM_POST,
                lti_contexts__id=context.id,
            )
            # If course is locked, security to remove forum permission on default group
            # only needed if the course has been marked outside web navigation
            if context.is_marked_locked and any(
                item in DEFAULT_FORUM_BASE_READ_PERMISSIONS
                for item in GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_base_group(), has_perm=True
                ).values_list("permission__codename", flat=True)
            ):
                for perm in DEFAULT_FORUM_BASE_WRITE_PERMISSIONS:
                    remove_perm(perm, context.get_base_group(), forum)

        except Forum.DoesNotExist:

            # Check if this uuid exists for another context.id to reuse its name as a
            # default value (enables copy and paste)
            forum_same_uuid = (
                Forum.objects.only("name")
                .filter(lti_id=forum_uuid, type=Forum.FORUM_POST)
                .order_by("-created")
                .first()
            )

            forum = Forum.objects.create(
                lti_id=forum_uuid,
                type=Forum.FORUM_POST,
                name=forum_same_uuid.name
                if forum_same_uuid
                else lti_request.context_title,
            )
            logger.debug("Forum %s created", forum_uuid)
            self._init_forum(forum, context)

        if not getattr(self.request.user, "public_username", ""):
            redirect_url = reverse("forum.username.change")
        else:
            redirect_url = reverse(
                "forum:forum", kwargs={"slug": forum.slug, "pk": forum.id}
            )

        response = HttpResponseRedirect(redirect_url)

        locale = lti_request.get_param("launch_presentation_locale")
        if locale:
            logger.debug("Course locale detected %s", locale)
            translation.activate(locale)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, locale)

        return response

    def _init_forum(self, forum, context):
        """
        Initialize a forum.

        This method sets default permissions according to the LTI context that
        initiated the creation of the forum.
        """
        forum.lti_contexts.add(context)
        # only assign full permissions if the course is not marked as locked
        self._assign_permissions(
            forum,
            context.get_base_group(),
            DEFAULT_FORUM_BASE_PERMISSIONS
            if not context.is_marked_locked
            else DEFAULT_FORUM_BASE_READ_PERMISSIONS,
        )

        # pylint: disable=no-member
        for role, perms in DEFAULT_FORUM_ROLES_PERMISSIONS.items():
            self._assign_permissions(forum, context.get_role_group(role), perms)

    @staticmethod
    def _assign_permissions(forum, group, permissions: List[str]):
        """Grant a list of permissions for a group on a specific forum."""
        for perm in permissions:
            logger.debug(
                "Grant permission %s to group %s on forum %s",
                perm,
                group.name,
                forum.lti_id,
            )
            assign_perm(perm, group, forum, True)


class ChangeUsernameView(PermissionRequiredMixin, UpdateView):
    """Allow the current user to update his username."""

    model = User
    fields = ["public_username"]
    template_name = "ashley/change_username.html"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        # pylint: disable=attribute-defined-outside-init
        self.object = form.save()
        messages.success(
            self.request,
            _(
                f"Welcome {self.request.user.public_username}, your username is now registered."
            ),
        )
        return HttpResponseRedirect(reverse("forum:index"))

    # pylint: disable=no-self-use,unused-argument
    def perform_permissions_check(self, user, obj, perms):
        """The user can update his username only if it is not yet defined"""
        return user.is_authenticated and not getattr(obj, "public_username", "")


class ManageModeratorsView(ManageModeratorPermission, TemplateView):
    """View to manage revoke and promote moderators."""

    context_object_name = "users"
    template_name = "ashley/manage_moderator.html"
