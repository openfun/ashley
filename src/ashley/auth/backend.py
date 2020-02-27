"""Authentication backend for ashley"""

from django.core.exceptions import PermissionDenied

from fun_lti_provider.default.backend import LTIBackend as BaseLTIBackend
from fun_lti_provider.lti import LTI


class LTIBackend(BaseLTIBackend):
    """
    Authentication backend using LTI launch request to authenticate an user.
    If a user does not exist in database, it creates it.
    The username is generated with the remote (consumer) user id and with
    the consumer identifier, to be able to authenticate users from multiple
    consumer sites without any collision.
    """

    def get_username_from_lti_request(self, lti_request: LTI) -> str:
        """
        Retrieve the username from the LTI request.

        The username is based on the remote user id and the corresponding LTI consumer
        It allows ashley to authenticate users from multiple consumer sites.

        Args:
            lti_request: The verified LTI request

        Returns:
            str: The username
        """
        remote_user_id = self._get_mandatory_param(lti_request, "user_id")

        lti_consumer = lti_request.get_consumer()
        if not lti_consumer:
            raise PermissionDenied
        username = "{:s}@{:s}".format(remote_user_id, lti_consumer.slug)
        return username
