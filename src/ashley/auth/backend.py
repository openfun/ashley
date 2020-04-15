"""Authentication backend for Ashley"""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied

from lti_provider.default.backend import LTIBackend as BaseLTIBackend
from lti_provider.lti import LTI

logger = logging.getLogger(__name__)


class LTIBackend(BaseLTIBackend):
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

        email = self._get_mandatory_param(
            lti_request, "lis_person_contact_email_primary"
        )
        remote_person_sourcedid = self._get_mandatory_param(
            lti_request, "lis_person_sourcedid"
        )

        logger.debug(
            "User %s (consumer = %s) authenticated from LTI request",
            username,
            lti_consumer.slug,
        )
        user_model = get_user_model()
        try:
            return user_model.objects.get(
                lti_consumer=lti_consumer, lti_remote_user_id=remote_person_sourcedid
            )
        except user_model.DoesNotExist:
            username = f"{remote_person_sourcedid}@{lti_consumer.slug:s}"

            user = user_model.objects.create_user(
                username,
                email=email,
                lti_consumer=lti_consumer,
                lti_remote_user_id=remote_person_sourcedid,
                public_username=remote_person_sourcedid,
            )
            logger.debug("User %s created in database", username)

        if not user.is_active:
            logger.debug("User %s is not active", user.username)
            raise PermissionDenied()
        return user
