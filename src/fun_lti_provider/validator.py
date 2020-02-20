"""
This module is an implementation of logic needed for checking
OAuth 1.0 signed LTI launch requests.


It is based on the work of django-lti-provider-auth
(https://github.com/wachjose88/django-lti-provider-auth)

Here is the original licence :

Copyright (c) 2018 Josef Wachtler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""
from oauthlib.oauth1 import RequestValidator

from .models import LTIPassport


class LTIRequestValidator(RequestValidator):
    """
    This validator implements the RequestValidator from the oauthlib, but only with methods
    required for a LTI launch request.
    """

    @property
    def enforce_ssl(self):
        """
        Returns:
            bool: True if SSL is mandatory, False otherwise
        """
        return False

    @property
    def nonce_length(self):
        """
        Returns:
            tuple: A tuple containing the min and max length of a nonce
        """
        return 5, 50

    @property
    def dummy_client(self):
        """Dummy client used when an invalid client key is supplied.

        Returns:
            string: The dummy client key string.
        """
        return "dummy_client_key_123456"

    def get_client_secret(self, client_key, request):
        """Retrieves the client secret associated with the client key.

        If an unknown client_key is given, it returns a valid dummy secret in
        order to avoid timing attacks.

        This method must allow the use of a dummy client_key value.
        Fetching the secret using the dummy key must take the same amount of
        time as fetching a secret for a valid client::

        Args:
            client_key: The client/consumer key.
            request: The calling request.
        """

        try:
            passport = LTIPassport.objects.get(
                oauth_consumer_key=client_key, is_enabled=True
            )
            return passport.shared_secret
        except LTIPassport.DoesNotExist:
            return "dummy_client_sec_123456"

    def validate_client_key(self, client_key, request):
        """Validates that supplied client key is a registered and valid client.

        Args:
            client_key: The client/consumer key.
            request: The calling request

        Returns:
            bool: True if the client key is registered and valid
        """
        try:
            passports_count = LTIPassport.objects.filter(
                oauth_consumer_key=client_key, is_enabled=True
            ).count()
            return passports_count > 0
        except LTIPassport.DoesNotExist:
            return False

    # pylint: disable=too-many-arguments
    def validate_timestamp_and_nonce(
        self,
        client_key,
        timestamp,
        nonce,
        request,
        request_token=None,
        access_token=None,
    ):
        """Validates that the nonce has not been used before

        Per `Section 3.3`_ of the OAuth 1.0 spec.

        "A nonce is a random string, uniquely generated by the client to allow
        the server to verify that a request has never been made before and
        helps prevent replay attacks when requests are made over a non-secure
        channel.  The nonce value MUST be unique across all requests with the
        same timestamp, client credentials, and token combinations."

        .. _`Section 3.3`: https://tools.ietf.org/html/rfc5849#section-3.3

        One of the first validation checks that will be made is for the validity
        of the nonce and timestamp, which are associated with a client key and
        possibly a token. If invalid then immediately fail the request
        by returning False. If the nonce/timestamp pair has been used before and
        you may just have detected a replay attack. Therefore it is an essential
        part of OAuth security that you not allow nonce/timestamp reuse.
        Note that this validation check is done before checking the validity of
        the client and token.::

        Args:
            client_key: The client/consumer key.
            timestamp: The ``oauth_timestamp`` request parameter.
            nonce: The ``oauth_nonce`` request parameter.
            request: The calling request
            request_token: Request token string, if any.
            access_token: Access token string, if any.

        Returns:
            bool: True if the timestamp and nonce has not been used before
        """
        # pylint: disable=fixme
        # TODO: Implement this with a redis server (to have an expiration mechanism) \
        #  or with a database model, with a cron cleaning older entries.
        return True
