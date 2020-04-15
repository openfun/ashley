"""Views of the ashley django application."""

import logging
from typing import List

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.utils import translation
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from lti_provider.lti import LTI
from lti_provider.views import BaseLTIView

from .defaults import DEFAULT_FORUM_BASE_PERMISSIONS, DEFAULT_FORUM_ROLES_PERMISSIONS

Forum = get_model("forum", "Forum")  # pylint: disable=C0103
LTIContext = get_model("ashley", "LTIContext")  # pylint: disable=C0103

logger = logging.getLogger(__name__)


class ForumLTIView(BaseLTIView):
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

        forum_uuid = self.kwargs["uuid"]
        forum, forum_created = Forum.objects.get_or_create(
            lti_id=forum_uuid,
            type=Forum.FORUM_POST,
            defaults={"name": lti_request.context_title},
        )
        if forum_created:
            logger.debug("Forum %s created", forum_uuid)
            self._init_forum(forum, context)

        response = HttpResponseRedirect(
            reverse("forum:forum", kwargs={"slug": forum.slug, "pk": forum.id})
        )

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
        self._assign_permissions(
            forum, context.get_base_group(), DEFAULT_FORUM_BASE_PERMISSIONS,
        )
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
