"""
Utilities to represent and validate LTI Launch parameters

This is based on lti library (https://github.com/pylti/lti).
"""
from collections.abc import MutableMapping
from typing import List, Union
from urllib.parse import urlencode

DEFAULT_LTI_VERSION = "LTI-1.0"

LAUNCH_PARAMS_REQUIRED = ["lti_message_type", "lti_version", "resource_link_id"]

LAUNCH_PARAMS_RECOMMENDED = [
    "resource_link_description",
    "resource_link_title",
    "user_id",
    "user_image",
    "roles",
    "lis_person_name_given",
    "lis_person_name_family",
    "lis_person_name_full",
    "lis_person_contact_email_primary",
    "role_scope_mentor",
    "context_id",
    "context_label",
    "context_title",
    "context_type",
    "launch_presentation_locale",
    "launch_presentation_document_target",
    "launch_presentation_css_url",
    "launch_presentation_width",
    "launch_presentation_height",
    "launch_presentation_return_url",
    "tool_consumer_info_product_family_code",
    "tool_consumer_info_version",
    "tool_consumer_instance_guid",
    "tool_consumer_instance_name",
    "tool_consumer_instance_description",
    "tool_consumer_instance_url",
    "tool_consumer_instance_contact_email",
]

LAUNCH_PARAMS_LIS = [
    "lis_course_section_sourcedid",
    "lis_course_offering_sourcedid",
    "lis_outcome_service_url",
    "lis_person_sourcedid",
    "lis_result_sourcedid",
]

LAUNCH_PARAMS_RETURN_URL = ["lti_errormsg", "lti_errorlog", "lti_msg", "lti_log"]

LAUNCH_PARAMS_OAUTH = [
    "oauth_consumer_key",
    "oauth_signature_method",
    "oauth_timestamp",
    "oauth_nonce",
    "oauth_version",
    "oauth_signature",
    "oauth_callback",
    "oauth_token",
]

LAUNCH_PARAMS_IS_LIST = [
    "roles",
    "role_scope_mentor",
    "context_type",
    "accept_media_types",
    "accept_presentation_document_targets",
]

LAUNCH_PARAMS_CANVAS = ["selection_directive", "text"]

CONTENT_PARAMS_REQUEST = [
    "accept_media_types",
    "accept_presentation_document_targets",
    "content_item_return_url",
    "accept_unsigned",
    "accept_multiple",
    "accept_copy_advice",
    "auto_create",
    "title",
    "data",
    "can_confirm",
]

CONTENT_PARAMS_RESPONSE = [
    "content_items",
    "lti_msg",
    "lti_log",
    "lti_errormsg",
    "lti_errorlog",
]

REGISTRATION_PARAMS = ["tc_profile_url", "reg_password", "reg_key"]

LAUNCH_PARAMS = (
    LAUNCH_PARAMS_REQUIRED
    + LAUNCH_PARAMS_RECOMMENDED
    + LAUNCH_PARAMS_RETURN_URL
    + LAUNCH_PARAMS_OAUTH
    + LAUNCH_PARAMS_LIS
    + LAUNCH_PARAMS_CANVAS
    + CONTENT_PARAMS_REQUEST
    + CONTENT_PARAMS_RESPONSE
    + REGISTRATION_PARAMS
)


class LaunchParams(MutableMapping):
    """
    Represents the params for an LTI launch request. Provides dict-like
    behavior through the use of the MutableMapping ABC mixin.  Strictly
    enforces that params are valid LTI params.
    """

    def __init__(self, *args, **kwargs):

        self._params = dict()
        self.update(*args, **kwargs)

        # now verify we only got valid launch params
        for k in self.keys():
            if not self.valid_param(k):
                raise InvalidLaunchParamException(k)

        for param in LAUNCH_PARAMS_REQUIRED:
            if param not in self:
                raise MissingLaunchParamException(param)

    def _param_value(self, param: str) -> Union[str, List]:
        """Get the value of a LTI parameter

        Args:
            param: LTI parameter name

        Returns:
            The value of the LTI parameter, as a str or a List, depending on the parameter.
        """
        if param in LAUNCH_PARAMS_IS_LIST:
            return [x.strip() for x in self._params[param].split(",")]
        return self._params[param]

    @staticmethod
    def valid_param(param: str) -> bool:
        """Checks if a LTI parameter is valid or not

        Args:
            param: LTI parameter name

        Returns:
            bool: True if the parameter is valid, False otherwise.

        """
        if param.startswith("custom_") or param.startswith("ext_"):
            return True
        return param in LAUNCH_PARAMS

    def __len__(self):
        return len(self._params)

    def __getitem__(self, item):
        if not self.valid_param(item):
            raise KeyError("{} is not a valid launch param".format(item))
        try:
            return self._param_value(item)
        except KeyError:
            # catch and raise new KeyError in the proper context
            raise KeyError(item)

    def __setitem__(self, key, value):
        if not self.valid_param(key):
            raise InvalidLaunchParamException(key)
        if key in LAUNCH_PARAMS_IS_LIST:
            if isinstance(value, list):
                value = ",".join([x.strip() for x in value])
        self._params[key] = value

    def __delitem__(self, key):
        if key in self._params:
            del self._params[key]

    def __iter__(self):
        return iter(self._params)

    @property
    def urlencoded(self) -> str:
        """Get the URL encoded representation of the LTI parameter list

        Returns:
            str: URL encoded LTI parameters
        """
        params = dict(self)
        # stringify any list values
        for key, value in params.items():
            if isinstance(value, list):
                params[key] = ",".join(value)
        return urlencode(params)


class LaunchParamException(Exception):
    """Custom Exception related to LTI launch param processing"""


class InvalidLaunchParamException(LaunchParamException):
    """Custom Exception thrown when an invalid parameter is found in a LTI launch request"""

    def __init__(self, param):
        message = "{} is not a valid launch param".format(param)
        super().__init__(message)


class MissingLaunchParamException(LaunchParamException):
    """Custom Exception thrown when a required LTI parameter is missing in an LTI launch request"""

    def __init__(self, param):
        message = "missing launch param : {}".format(param)
        super().__init__(message)
