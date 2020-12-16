"""Test suite for ashley authentication backend."""

from urllib.parse import unquote, urlencode

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory, TestCase
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from lti_toolbox.lti import LTI
from lti_toolbox.models import LTIPassport
from oauthlib import oauth1

from ashley.auth.backend import LTIBackend

CONTENT_TYPE = "application/x-www-form-urlencoded"


class LTIBackendTestCase(TestCase):
    """Test the LTIBackend class"""

    def setUp(self):
        """Override the setUp method to instanciate and serve a request factory."""
        super().setUp()
        self.request_factory = RequestFactory()
        self._auth_backend = LTIBackend()

    @staticmethod
    def _sign_parameters(passport, lti_parameters, url):
        """

        Args:
            passport: The LTIPassport to use to sign the oauth request
            lti_parameters: A dictionnary of parameters to sign
            url: The LTI launch URL

        Returns:
            dict: The signed parameters
        """

        signed_parameters = lti_parameters.copy()
        oauth_client = oauth1.Client(
            client_key=passport.oauth_consumer_key, client_secret=passport.shared_secret
        )
        # Compute Authorization header which looks like:
        # Authorization: OAuth oauth_nonce="80966668944732164491378916897",
        # oauth_timestamp="1378916897", oauth_version="1.0", oauth_signature_method="HMAC-SHA1",
        # oauth_consumer_key="", oauth_signature="frVp4JuvT1mVXlxktiAUjQ7%2F1cw%3D"
        _uri, headers, _body = oauth_client.sign(
            url,
            http_method="POST",
            body=lti_parameters,
            headers={"Content-Type": CONTENT_TYPE},
        )

        # Parse headers to pass to template as part of context:
        oauth_dict = dict(
            param.strip().replace('"', "").split("=")
            for param in headers["Authorization"].split(",")
        )

        signature = oauth_dict["oauth_signature"]
        oauth_dict["oauth_signature"] = unquote(signature)
        oauth_dict["oauth_nonce"] = oauth_dict.pop("OAuth oauth_nonce")
        signed_parameters.update(oauth_dict)
        return signed_parameters

    def _authenticate(
        self,
        lti_parameters: dict,
        passport: LTIPassport,
    ):
        url = "http://testserver/lti/launch"
        signed_parameters = self._sign_parameters(passport, lti_parameters, url)
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
                "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
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
                "user_id": "1c6cd9c1-ca4c-41fe-b369-912075a5d3ce",
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

        # Missing param : lis_person_sourcedid or ext_user_username or user_id
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

    def test_optional_public_username(self):
        """
        Ensure that we can authenticate with success if the public username is
        not found in the LTI request
        """

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        user_count = get_user_model().objects.count()

        new_user = self._authenticate(
            {
                "user_id": "3fd0ff83-a62d-4a12-9716-4d48821ae24f",
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "aaa",
                "context_id": "course-v1:fooschool+authbackend+0001",
                "lis_person_contact_email_primary": "user_without_username@example.com",
            },
            passport,
        )

        self.assertEqual("", new_user.public_username)
        self.assertEqual(consumer, new_user.lti_consumer)
        self.assertEqual("user_without_username@example.com", new_user.email)
        self.assertEqual(
            "3fd0ff83-a62d-4a12-9716-4d48821ae24f@consumer", new_user.username
        )
        self.assertEqual(user_count + 1, get_user_model().objects.count())

    def test_optional_email(self):
        """
        Ensure that we can authenticate with success if the user email is
        not found in the LTI request
        """

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        user_count = get_user_model().objects.count()

        new_user = self._authenticate(
            {
                "user_id": "7275a984-1e77-4084-9fe6-e54d0deba0e7",
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "aaa",
                "context_id": "course-v1:fooschool+authbackend+0001",
                "lis_person_sourcedid": "user_without_email",
            },
            passport,
        )

        self.assertEqual("user_without_email", new_user.public_username)
        self.assertEqual("", new_user.email)
        self.assertEqual(consumer, new_user.lti_consumer)
        self.assertEqual("user_without_email@consumer", new_user.username)
        self.assertEqual(user_count + 1, get_user_model().objects.count())

    def test_openedx_studio_launch_request(self):
        """
        Ensure that a launch request initiated by OpenedX studio is accepted by the
        authentication backend AND that a user_id specific to the context_id is
        generated.
        """

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        user_count = get_user_model().objects.count()

        # User 1 is using ashley from openedx studio in the course "TEST1"
        user1 = self._authenticate(
            {
                "context_id": "course-v1:TEST1+0001+2020_T1",
                "context_label": "TEST1",
                "context_title": "test course 1",
                "custom_component_display_name": "Forum",
                "launch_presentation_return_url": "",
                "lis_result_sourcedid": "course-v1%3ATEST1%2B0001%2B2020_T1:-c7b2c44b1d",
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "-c7b2c44b1d",
                "roles": "Instructor",
                "user_id": "student",
            },
            passport,
        )

        # A new ashley user should have been created
        self.assertEqual(user_count + 1, get_user_model().objects.count())
        self.assertEqual("", user1.public_username)
        self.assertEqual("", user1.email)
        self.assertEqual(consumer, user1.lti_consumer)
        self.assertNotEqual("student@consumer", user1.username)

        # User 2 is using ashley from openedx studio in the course "TEST1"
        # (it is basically the same LTI launch request than user 1)
        user2 = self._authenticate(
            {
                "context_id": "course-v1:TEST1+0001+2020_T1",
                "context_label": "TEST1",
                "context_title": "test course 1",
                "custom_component_display_name": "Forum",
                "launch_presentation_return_url": "",
                "lis_result_sourcedid": "course-v1%3ATEST1%2B0001%2B2020_T1:-c7b2c44b1d",
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "-c7b2c44b1d",
                "roles": "Instructor",
                "user_id": "student",
            },
            passport,
        )

        # user1 and user2 should be the same. No new user should have been created, since they
        # came from the same LTI context_id.
        self.assertEqual(user_count + 1, get_user_model().objects.count())
        self.assertEqual(user1, user2)

        # User 3 is using ashley from openedx studio in the course "TEST2"
        user3 = self._authenticate(
            {
                "context_id": "course-v1:TEST2+0001+2020_T1",
                "context_label": "TEST2",
                "context_title": "test course 2",
                "custom_component_display_name": "Forum",
                "launch_presentation_return_url": "",
                "lis_result_sourcedid": "course-v1%3ATEST2%2B0001%2B2020_T1:-a2a2a2a2a2",
                "lti_message_type": "basic-lti-launch-request",
                "lti_version": "LTI-1p0",
                "resource_link_id": "-a2a2a2a2a2",
                "roles": "Instructor",
                "user_id": "student",
            },
            passport,
        )
        # A new ashley user should have been created for user 3
        self.assertEqual(user_count + 2, get_user_model().objects.count())
        self.assertEqual("", user3.public_username)
        self.assertEqual("", user3.email)
        self.assertEqual(consumer, user3.lti_consumer)
        self.assertNotEqual("student@consumer", user3.username)
        self.assertNotEqual(user1, user3)

    def test_moodle_launch_request(self):
        """
        Ensure that a launch request initiated by Moodle is
        accepted by the authentication backend.
        """

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        new_user = self._authenticate(
            {
                "user_id": "2",
                "lis_person_sourcedid": "",
                "roles": (
                    "Instructor,urn:lti:sysrole:ims/lis/Administrator,"
                    + "urn:lti:instrole:ims/lis/Administrator"
                ),
                "context_id": "2",
                "context_label": "moodle101",
                "context_title": "Moodle 101",
                "resource_link_title": "Test forum 2",
                "resource_link_description": "",
                "resource_link_id": "2",
                "context_type": "CourseSection",
                "lis_course_section_sourcedid": "",
                "lis_result_sourcedid": (
                    '{"data":{"instanceid":"2","userid":"2","typeid":"1","launchid":1424835319}, '
                    + '"hash":"2d521baae5180acbc4ea200dfa3f4c75176010b16b0be666cba68a882c7caa82"}'
                ),
                "lis_outcome_service_url": "http://moodle-instance.example/mod/lti/service.php",
                "lis_person_name_given": "Admin",
                "lis_person_name_family": "User",
                "lis_person_name_full": "Admin User",
                "ext_user_username": "moodle-user",
                "lis_person_contact_email_primary": "user@example.com",
                "launch_presentation_locale": "en",
                "ext_lms": "moodle-2",
                "tool_consumer_info_product_family_code": "moodle",
                "tool_consumer_info_version": "2019111802",
                "lti_version": "LTI-1p0",
                "lti_message_type": "basic-lti-launch-request",
                "tool_consumer_instance_guid": "mooodle-instance.example",
                "tool_consumer_instance_name": "Test Site",
                "tool_consumer_instance_description": "Test Site",
                "launch_presentation_document_target": "iframe",
                "launch_presentation_return_url": (
                    "http://moodle-instance.example/mod/lti/return.php"
                    + "?course=2&launch_container=3&instanceid=2&sesskey=TEST"
                ),
            },
            passport,
        )

        self.assertEqual("moodle-user", new_user.public_username)
