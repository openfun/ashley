"""Authentication backend for Ashley"""
import hashlib
import logging
from typing import List

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
from lti_toolbox.backend import LTIBackend as ToolboxLTIBackend
from lti_toolbox.lti import LTI

from ashley.defaults import _FORUM_ROLE_ADMINISTRATOR, _FORUM_ROLE_INSTRUCTOR

logger = logging.getLogger(__name__)


class LTIBackend(ToolboxLTIBackend):
    """
    Authentication backend using LTI launch request to authenticate a user.
    If a user does not exist in database, it creates it.
    The username is generated with the remote (consumer) user id and with
    the consumer identifier, to be able to authenticate users from multiple
    consumer sites without any collision.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        lti_request: LTI = kwargs.get("lti_request")
        if not lti_request:
            return None

        if not lti_request.is_valid:
            raise PermissionDenied()

        lti_consumer = lti_request.get_consumer()
        if not lti_consumer:
            raise PermissionDenied

        remote_user_id = self._get_remote_user_id(lti_request)

        # Try to get optional values from LTI request
        email = lti_request.get_param("lis_person_contact_email_primary", "")
        public_username = self._get_public_username(lti_request)

        # Handle special case for OpenedX studio :
        # When OpenedX studio initiates a LTI request to render ashley in a
        # xblock, it always sends "student" as the user_id. This is a problem,
        # because all openedX studio users of the same LTI consumer would
        # share the same user account on ashley. And they would have an
        # instructor access to every forums related to their LTI consumer.
        # To resolve this problem, we generate a user id based on the
        # context_id.
        if self._is_open_edx_studio(lti_request):
            context_id = self._get_mandatory_param(lti_request, "context_id")
            # generate an identifier in a normalized format, based on the context id
            # pylint: disable=too-many-function-args
            generated_id = hashlib.shake_128(context_id.encode("utf-8")).hexdigest(20)
            remote_user_id = f"openedxstudio-{generated_id}"

        logger.debug(
            "User %s (consumer = %s) authenticated from LTI request",
            remote_user_id,
            lti_consumer.slug,
        )
        user_model = get_user_model()
        try:
            user = user_model.objects.get(
                lti_consumer=lti_consumer, lti_remote_user_id=remote_user_id
            )
            # if public_username is empty we set it to a default value
            if not user.public_username and any(
                role in [_FORUM_ROLE_ADMINISTRATOR, _FORUM_ROLE_INSTRUCTOR]
                for role in lti_request.roles
            ):
                user.public_username = self._get_public_username_default(lti_request)
                user.save()

        except user_model.DoesNotExist:
            username = f"{remote_user_id}@{lti_consumer.slug:s}"

            user = user_model.objects.create_user(
                username,
                email=email,
                lti_consumer=lti_consumer,
                lti_remote_user_id=remote_user_id,
                public_username=public_username,
            )
            logger.debug("User %s created in database", username)

        if not user.is_active:
            logger.debug("User %s is not active", user.username)
            raise PermissionDenied()
        return user

    def _get_remote_user_id(self, lti_request: LTI):
        """
        Get the remote unique user identifier.
        It can be in different LTI parameters, depends on the LTI consumer.
        """
        user_id = self._get_lti_param_with_fallback(
            lti_request,
            [
                # OpenEdx
                "lis_person_sourcedid",
                # Moodle
                "ext_user_username",
                # Fallback to anonymous user_id
                "user_id",
            ],
        )
        if user_id:
            return user_id
        logger.debug("Unable to find remote user id in LTI request")
        raise PermissionDenied()

    def _get_public_username(self, lti_request: LTI):
        """
        Try to get a human-friendly remote user id in the LTI request.
        It tries different LTI parameters, because it depends on the LTI consumer.
        If not found, it returns ""
        """
        return self._get_lti_param_with_fallback(
            lti_request,
            [
                # OpenEdx
                "lis_person_sourcedid",
                # Moodle
                "ext_user_username",
            ],
            default_value=self._get_public_username_default(lti_request),
        )

    @staticmethod
    def _get_public_username_default(lti_request: LTI):
        """
        Return a default username for an LTI request depending of the user's role.
        """
        if _FORUM_ROLE_INSTRUCTOR in lti_request.roles:
            return _("Educational team")
        if _FORUM_ROLE_ADMINISTRATOR in lti_request.roles:
            return _("Administrator")

        return ""

    @staticmethod
    def _get_lti_param_with_fallback(
        lti_request: LTI, parameter_names: List[str], default_value=None
    ):
        """
        Depending on the LTI consumer, LTI parameters name can differ for the same value.
        This utility method allows to search for a value in the LTI request, by giving multiple
        parameter names, by order of preference.

        Args:
            lti_request: the LTI request
            parameter_names: The name of the LTI parameters to get, by order of preference
            default_value: value returned if none of these LTI parameters is found

        Returns:
            The value found in the LTI request, or default_value otherwise

        """
        for param in parameter_names:
            value = lti_request.get_param(param)
            if value:
                return value
        return default_value

    @staticmethod
    def _is_open_edx_studio(lti_request):
        """
        Detects if the LTI launch request is coming from OpenedX studio.
        """
        return (
            lti_request.get_param("user_id") == "student"
            and not lti_request.get_param("lis_person_contact_email_primary")
            and not lti_request.get_param("lis_person_sourcedid")
            and not lti_request.get_param("ext_user_username")
            and lti_request.roles == ["instructor"]
        )
