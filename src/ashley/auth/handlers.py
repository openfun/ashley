"""This module contains default handlers for LTI launch request"""
import logging

from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseRedirect,
)
from django.urls import reverse
from django.utils import translation
from machina.core.db.models import get_model

from lti_provider.exceptions import LTIException
from lti_provider.lti import LTI

from ..permissions.groups import (
    GroupType,
    build_forum_group_name,
    sync_forum_user_groups,
)

Forum = get_model("forum", "Forum")  # pylint: disable=C0103

logger = logging.getLogger("ashley")


# pylint: disable=unused-argument
def success(request: HttpRequest, lti_request: LTI) -> HttpResponse:
    """
    Handler for successfully verified LTI launch requests.

    First, it calls the authentication backends to try to authenticate
    the user with the LTI request.

    It will then redirect the user to the right forum, or
    display an error message.

    Args:
        request: The HTTP request
        lti_request: The verified LTI request

    Returns:
        HttpResponse: An HTTP response
    """

    user = authenticate(request, lti_request=lti_request)
    if user is not None:

        # Get the context_id (course identifier) of the LTI request
        lti_context = lti_request.get_param("context_id")
        if not lti_context:
            return HttpResponseBadRequest()

        login(request, user)

        # Get the forum related to this context id
        course_forum, _created = Forum.objects.get_or_create(
            lti_consumer=lti_request.get_consumer(),
            lti_context=lti_context,
            type=Forum.FORUM_POST,
            defaults={"name": lti_request.context_title, "type": Forum.FORUM_POST},
        )

        # Synchronize group membership
        user_groups = map(
            lambda role: build_forum_group_name(course_forum.id, GroupType.ROLE, role),
            lti_request.roles,
        )
        sync_forum_user_groups(user, course_forum, list(user_groups))

        response = HttpResponseRedirect(
            reverse(
                "forum:forum", kwargs={"slug": course_forum.slug, "pk": course_forum.id}
            )
        )

        course_locale = lti_request.get_param("launch_presentation_locale")
        if course_locale:
            logger.debug("Course locale detected %s", course_locale)
            translation.activate(course_locale)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, course_locale)

        return response

    return HttpResponseForbidden("Forbidden")


# pylint: disable=unused-argument
def failure(request: HttpRequest, error: LTIException) -> HttpResponse:
    """
    Default handler for invalid LTI launch requests.
    You are encouraged to define your own handler according to your project needs.

    See LTI_LAUNCH_FAILURE_HANDLER setting.

    Args:
        request: the HTTP request
        error: The LTIException encountered

    Returns:
        HttpResponse: An HTTP response
    """
    return HttpResponseForbidden("Invalid LTI launch request")
