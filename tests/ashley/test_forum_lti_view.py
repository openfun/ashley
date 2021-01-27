"""Test suite for ashley ForumLTIView."""

from urllib.parse import urlencode

from django.conf import settings
from django.test import TestCase
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from machina.core.db.models import get_model

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import UserFactory

from tests.ashley.lti_utils import CONTENT_TYPE, sign_parameters

Forum = get_model("forum", "Forum")
LTIContext = get_model("ashley", "LTIContext")


class ForumLTIViewTestCase(TestCase):
    """Test the ForumLTIView class"""

    def test_post_with_valid_lti_launch_request(self):
        """A user should be able to authenticate via a LTI launch request signed by
        a trusted consumer and passport."""

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
        context_id = "course-v1:testschool+login+0001"

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": context_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": "testuser",
            "launch_presentation_locale": "en",
            "roles": "Instructor",
        }
        url = f"http://testserver/lti/forum/{forum_uuid}"
        signed_parameters = sign_parameters(passport, lti_parameters, url)

        response = self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )

        # A LTIContext and a Forum should have been created
        context = LTIContext.objects.get(lti_id=context_id)
        forum = Forum.objects.get(lti_id=forum_uuid)

        # The response should be a redirection to the forum URL
        self.assertEqual(302, response.status_code)
        self.assertEqual(f"/forum/forum/{forum.slug}-{forum.id}/", response.url)

        # Our current LTIContext id should have been injected in the user session
        self.assertEqual(context.id, self.client.session.get(SESSION_LTI_CONTEXT_ID))

        # The launch_presentation_locale should be set in the language cookie
        self.assertEqual(
            "en", response.client.cookies[settings.LANGUAGE_COOKIE_NAME].value
        )

    def test_post_with_an_inactive_user(self):
        """An inactive user should not be allowed to authenticate via a valid LTI request"""

        user = UserFactory(is_active=False)
        passport = LTIPassportFactory(
            title="consumer1_passport1", consumer=user.lti_consumer
        )

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
        context_id = "course-v1:testschool+login+0001"

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": context_id,
            "lis_person_contact_email_primary": "inactive_test_user@example.com",
            "lis_person_sourcedid": user.public_username,
            "launch_presentation_locale": "en",
            "roles": "Instructor",
        }
        url = f"http://testserver/lti/forum/{forum_uuid}"
        signed_parameters = sign_parameters(passport, lti_parameters, url)

        response = self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )

        self.assertEqual(403, response.status_code)

    def test_get(self):
        """The GET method is not allowed to sign in"""

        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
        context_id = "course-v1:testschool+login+0001"

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": context_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": "testuser",
            "launch_presentation_locale": "en",
            "roles": "Instructor",
        }
        url = f"http://testserver/lti/forum/{forum_uuid}"
        signed_parameters = sign_parameters(passport, lti_parameters, url)

        response = self.client.get(
            f"/lti/forum/{forum_uuid}",
            data=signed_parameters,
            content_type=CONTENT_TYPE,
        )
        self.assertEqual(405, response.status_code)

    def test_put(self):
        """The PUT method is not allowed to sign in"""
        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
        context_id = "course-v1:testschool+login+0001"

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": context_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": "testuser",
            "launch_presentation_locale": "en",
            "roles": "Instructor",
        }
        url = f"http://testserver/lti/forum/{forum_uuid}"
        signed_parameters = sign_parameters(passport, lti_parameters, url)

        response = self.client.put(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )
        self.assertEqual(405, response.status_code)

    def test_delete(self):
        """The DELETE method is not allowed to sign in"""
        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
        context_id = "course-v1:testschool+login+0001"

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": context_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": "testuser",
            "launch_presentation_locale": "en",
            "roles": "Instructor",
        }
        url = f"http://testserver/lti/forum/{forum_uuid}"
        signed_parameters = sign_parameters(passport, lti_parameters, url)

        response = self.client.delete(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )
        self.assertEqual(405, response.status_code)
