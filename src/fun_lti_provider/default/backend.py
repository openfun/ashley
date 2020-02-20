"""This module contains an example authentication backend for django
"""

import logging
from typing import Any, Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest

from fun_lti_provider.lti import LTI

logger = logging.getLogger("fun_lti_provider")
USER_MODEL = get_user_model()


class LTIBackend:
    """
    Authentication backend used by fun_lti_provider.default.handlers.success handler
    It authenticates an user from a verified LTI request and creates an User if necessary.

    You are encouraged to make your own authentication backend, by overriding this one to
    add your own domain logic.
    """

    def authenticate(self, request: Optional[HttpRequest], **kwargs):
        """
        Authenticate an user from a LTI request

        Args:
            request: django http request
            kwargs: additional parameters

        Returns:
            An authenticated user or None
        """

        lti_request = kwargs.get("lti_request")
        if not lti_request:
            return None

        if not self.check_lti_request_content(lti_request):
            return None

        username = self.get_username_from_lti_request(lti_request)
        logger.debug("User %s authenticated from LTI request", username)

        try:
            user = USER_MODEL.objects.get(username=username)
        except USER_MODEL.DoesNotExist:
            user = self.prepare_new_user(lti_request)
            user.save()
            logger.debug("User %s created in database", username)
        if not user:
            raise PermissionDenied
        return user

    def check_lti_request_content(self, lti_request) -> bool:
        """
        Verify that the LTI launch request contains enough information to log the user in.
        You should override this method with your own domain logic.

        Args:
            lti_request: The LTI request to verify

        Returns:
            bool: True if the LTI request is valid to authenticate the user, or False
            if the user can't be authenticated.

        Raises:
            PermissionDenied if the user cannot be authenticated and you dont't want to pass
            the LTI request to the next configured authentication middleware.
        """
        if not lti_request.is_valid:
            raise PermissionDenied

        # The LTI request must provide an unique identifier for the user
        self._get_mandatory_param(lti_request, "user_id")

        # The request must provide an email for the user
        self._get_mandatory_param(lti_request, "lis_person_contact_email_primary")

        return True

    # pylint: disable=no-self-use
    def get_username_from_lti_request(self, lti_request: LTI) -> str:
        """
        Retrieve the username from the LTI request.
        You have to ensure that this username is unique.

        You should override this method with your own domain logic.

        Args:
            lti_request: The verified LTI request

        Returns:
            str: The username
        """
        return lti_request.get_param("user_id")

    def prepare_new_user(self, lti_request):
        """
        Instantiate a new user (using USER_MODEL) from a LTI request

        Args:
            lti_request: the verified LTI request

        Returns:
            user: the new user to save

        """
        username = self.get_username_from_lti_request(lti_request)
        user = USER_MODEL(username=username)
        user.set_unusable_password()
        user.email = lti_request.get_param("lis_person_contact_email_primary")
        return user

    # pylint: disable=no-self-use
    # (errors disabled to keep the original prototype from django.contrib.auth.backend)
    def get_user(self, user_id):
        """
        Retrieve a user from database, given an id

        Args:
            user_id: the user id

        Returns:
            The user or None if not found
        """
        logger.debug("Trying to get user %s from database", user_id)
        try:
            user = USER_MODEL.objects.get(pk=user_id)
        except USER_MODEL.DoesNotExist:
            return None
        logger.debug("User found : %s", user.username)
        return user

    # pylint: disable=unused-argument,no-self-use
    # (errors disabled to keep the original prototype from django.contrib.auth.backend)
    def get_user_permissions(self, user_obj, obj=None):
        """
        Returns the set of permission strings the user_obj has from their own
        user permissions.

        See https://docs.djangoproject.com/en/2.2/ref/contrib/auth/

        This default implementation does not return any permissions.
        You should override it.
        """
        return set()

    # pylint: disable=unused-argument,no-self-use
    # (errors disabled to keep the original prototype from django.contrib.auth.backend)
    def get_group_permissions(self, user_obj, obj=None):
        """
        Return a set of permission strings the user `user_obj` has from the
        groups they belong.

        See https://docs.djangoproject.com/en/2.2/ref/contrib/auth/

        This default implementation does not return any permissions.
        You should override it.
        """
        return set()

    # pylint: disable=unused-argument,no-self-use
    # (errors disabled to keep the original prototype from django.contrib.auth.backend)
    def get_all_permissions(self, user_obj, obj=None):
        """
        Returns a set of permission strings that the user has, both through
        group and user permissions. If `obj` is passed in, only returns the
        permissions for this specific object.

        See https://docs.djangoproject.com/en/2.2/ref/contrib/auth/
        """
        return {
            *self.get_user_permissions(user_obj, obj=obj),
            *self.get_group_permissions(user_obj, obj=obj),
        }

    # pylint: disable=unused-argument,no-self-use
    # (errors disabled to keep the original prototype from django.contrib.auth.backend)
    def has_perm(self, user_obj, perm, obj=None):
        """
        Uses get_all_permissions() to check if user_obj has the permission string perm.

        See https://docs.djangoproject.com/en/2.2/ref/contrib/auth/
        """
        return perm in self.get_all_permissions(user_obj, obj=obj)

    @staticmethod
    def _get_mandatory_param(lti_request: LTI, param: str) -> Any:
        value = lti_request.get_param(param)
        if not value:
            logger.debug("Unable to find param %s in LTI request", param)
            raise PermissionDenied
        logger.debug("%s = %s", param, value)
        return value
