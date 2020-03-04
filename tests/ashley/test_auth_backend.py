"""Test suite for ashley authentication backend."""

from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase

from ashley.auth.backend import LTIBackend
from lti_provider.factories import LTIConsumerFactory, LTIPassportFactory
from lti_provider.lti import LTI
from lti_provider.models import LTIPassport

from tests.lti_provider.utils import CONTENT_TYPE, sign_parameters


class LTIBackendTestCase(TestCase):
    """Test the LTIBackend class"""

    def setUp(self):
        """Override the setUp method to instanciate and serve a request factory."""
        super().setUp()
        self.request_factory = RequestFactory()
        self._auth_backend = LTIBackend()

    def _authenticate(
        self, lti_parameters: dict, passport: LTIPassport,
    ):
        url = "http://testserver/lti/launch"
        signed_parameters = sign_parameters(passport, lti_parameters, url)
        request = self.request_factory.post(
            url, data=urlencode(signed_parameters), content_type=CONTENT_TYPE
        )
        lti = LTI(request)
        lti.verify()
        return self._auth_backend.authenticate(request, lti_request=lti)

    def test_known_user(self):
        """Test authentication with an already existing user."""

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        known_user = get_user_model().objects.create_user(
            "test_auth_backend_user1",
            email="ashley@example.com",
            public_username="ashley",
            lti_consumer=consumer,
            lti_remote_user_id="ashley",
        )

        user_count = get_user_model().objects.count()

        auth_user = self._authenticate(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "aaa",
                "context_id": "course-v1:fooschool+authbackend+0001",
                "lis_person_contact_email_primary": "ashley@example.com",
                "lis_person_sourcedid": "ashley",
            },
            passport,
        )
        self.assertEqual(known_user, auth_user)
        self.assertEqual(user_count, get_user_model().objects.count())

    def test_new_user(self):
        """Test authentication of a new user."""

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        user_count = get_user_model().objects.count()

        new_user = self._authenticate(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "aaa",
                "context_id": "course-v1:fooschool+authbackend+0001",
                "lis_person_contact_email_primary": "newuser@example.com",
                "lis_person_sourcedid": "new_user",
            },
            passport,
        )

        self.assertEqual("new_user", new_user.public_username)
        self.assertEqual(consumer, new_user.lti_consumer)
        self.assertEqual("newuser@example.com", new_user.email)
        self.assertEqual("new_user@consumer", new_user.username)
        self.assertEqual(user_count + 1, get_user_model().objects.count())

    def test_multiple_consumers(self):
        """
        Test to authenticate 2 users with the same username, coming from
        distinct consumer sites.
        """

        consumer1 = LTIConsumerFactory(slug="consumer1")
        passport_consumer1 = LTIPassportFactory(
            title="consumer1_passport", consumer=consumer1
        )

        consumer2 = LTIConsumerFactory(slug="consumer2")
        passport_consumer2 = LTIPassportFactory(
            title="consumer2_passport", consumer=consumer2
        )

        user1 = get_user_model().objects.create_user(
            "popular_username@test_auth_backend_consumer1",
            email="userc1@example.com",
            public_username="popular_username",
            lti_consumer=consumer1,
            lti_remote_user_id="popular_username",
        )

        user2 = get_user_model().objects.create_user(
            "popular_username@test_auth_backend_consumer2",
            email="userc2@example.com",
            public_username="popular_username",
            lti_consumer=consumer2,
            lti_remote_user_id="popular_username",
        )

        authenticated_user1 = self._authenticate(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "aaa",
                "context_id": "course-v1:fooschool+authbackend+0001",
                "lis_person_contact_email_primary": "userc1@example.com",
                "lis_person_sourcedid": "popular_username",
            },
            passport_consumer1,
        )

        authenticated_user2 = self._authenticate(
            {
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "aaa",
                "context_id": "course-v1:fooschool+authbackend+0001",
                "lis_person_contact_email_primary": "userc2@example.com",
                "lis_person_sourcedid": "popular_username",
            },
            passport_consumer2,
        )

        self.assertNotEqual(authenticated_user1, authenticated_user2)
        self.assertEqual(authenticated_user1, user1)
        self.assertEqual(authenticated_user2, user2)

    def test_required_parameters(self):
        """
        Ensure that authentication fails if parameters are missing in the LTI
        request.
        """

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        # Missing param : lis_person_sourcedid
        with self.assertRaises(PermissionDenied):
            self._authenticate(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "lti_version": "LTI-1p0",
                    "resource_link_id": "aaa",
                    "context_id": "course-v1:fooschool+authbackend+0001",
                    "lis_person_contact_email_primary": "ashley@example.com",
                },
                passport,
            )

        # Missing param : lis_person_contact_email_primary
        with self.assertRaises(PermissionDenied):
            self._authenticate(
                {
                    "lti_message_type": "basic-lti-launch-request",
                    "lti_version": "LTI-1p0",
                    "resource_link_id": "aaa",
                    "context_id": "course-v1:fooschool+authbackend+0001",
                    "lis_person_sourcedid": "ashley",
                },
                passport,
            )
