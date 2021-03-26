"""Test suite for ashley ForumLTIView."""
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import TestCase
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import UserFactory

from tests.ashley.lti_utils import CONTENT_TYPE, sign_parameters

Forum = get_model("forum", "Forum")
LTIContext = get_model("ashley", "LTIContext")
PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)


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

    def test_post_with_lti_uuid_forum_exiting_in_another_context(self):
        """
        Two forums can have an identical `lti_id` and be accessed from the same LTI
        launch URL but from two different LTI contexts. A new forum is created for
        each LTI context.
        """

        passport = LTIPassportFactory(consumer=LTIConsumerFactory())

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
        context1_id = "course-v1:testschool+login+0001"

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": context1_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": "testuser",
            "launch_presentation_locale": "en",
            "roles": "Instructor",
        }
        url = f"http://testserver/lti/forum/{forum_uuid}"
        # we sign the request
        initial_forum_count = Forum.objects.count()
        initial_lticontext_count = LTIContext.objects.count()
        response = self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(sign_parameters(passport, lti_parameters, url)),
            content_type=CONTENT_TYPE,
            follow=True,
        )

        # A LTIContext and a Forum should have been created
        context1 = LTIContext.objects.get(
            lti_id=context1_id, lti_consumer_id=passport.consumer
        )
        forum1 = Forum.objects.get(lti_id=forum_uuid, lti_contexts__id=context1.id)
        self.assertEqual(LTIContext.objects.count(), initial_lticontext_count + 1)
        self.assertEqual(Forum.objects.count(), initial_forum_count + 1)

        # The response should be a redirection to the forum URL
        self.assertRedirects(response, f"/forum/forum/{forum1.slug}-{forum1.id}/")

        # We use the same lti_parameters except the context
        context2_id = "course-v1:testschool+login+0002"
        lti_parameters2 = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963",
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": context2_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": "testuser",
            "launch_presentation_locale": "en",
            "roles": "Instructor",
        }
        # We request the same LTI launch source url
        response = self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(sign_parameters(passport, lti_parameters2, url)),
            content_type=CONTENT_TYPE,
            follow=True,
        )
        # A new lti context should have been created
        self.assertEqual(LTIContext.objects.count(), initial_lticontext_count + 2)
        # A new forum should have been created
        self.assertEqual(Forum.objects.count(), initial_forum_count + 2)
        # The response should be a redirection to the forum URL
        context2 = LTIContext.objects.get(
            lti_id=context2_id, lti_consumer_id=passport.consumer
        )
        forum2 = Forum.objects.get(lti_id=forum_uuid, lti_contexts__id=context2.id)
        self.assertRedirects(response, f"/forum/forum/{forum2.slug}-{forum2.id}/")

        # we resign the request for context1
        response = self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(sign_parameters(passport, lti_parameters, url)),
            content_type=CONTENT_TYPE,
            follow=True,
        )
        # No new lti context should have been created
        self.assertEqual(LTIContext.objects.count(), initial_lticontext_count + 2)
        # No new forum should have been created
        self.assertEqual(Forum.objects.count(), initial_forum_count + 2)
        # The response should be a redirection to the forum URL
        self.assertRedirects(response, f"/forum/forum/{forum1.slug}-{forum1.id}/")

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

    def test_groups_moderator_created_with_role_student(self):
        """
        Controls that group moderator is initialy created when a user login in the forum
        with the role student
        """
        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
        context_id = "course-v1:testschool+login+0001"
        initial_group_count = Group.objects.count()

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
            "roles": "Student",
        }
        url = f"http://testserver/lti/forum/{forum_uuid}"
        signed_parameters = sign_parameters(passport, lti_parameters, url)

        self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )

        # A LTIContext and a Forum should have been created
        context = LTIContext.objects.get(lti_id=context_id)

        # Groups should have been created
        self.assertEqual(initial_group_count + 5, Group.objects.count())
        self.assertEqual(
            [
                f"cg:{context.id}",
                f"cg:{context.id}:role:administrator",
                f"cg:{context.id}:role:instructor",
                f"cg:{context.id}:role:moderator",
                f"cg:{context.id}:role:student",
            ],
            list(
                Group.objects.filter(name__startswith=f"cg:{context.id}")
                .order_by("name")
                .values_list("name", flat=True)
            ),
        )

    def test_groups_moderator_created_with_role_instructor(self):
        """
        Controls that group moderator is initialy created when a user login as
        instructor in the forum
        """
        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd9"
        context_id = "course-v2:testschool+login+0001"
        initial_group_count = Group.objects.count()

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-433",
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

        self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )

        # A LTIContext has been created
        context = LTIContext.objects.get(lti_id=context_id)

        # Groups should have been created
        self.assertEqual(initial_group_count + 4, Group.objects.count())
        self.assertEqual(
            [
                f"cg:{context.id}",
                f"cg:{context.id}:role:administrator",
                f"cg:{context.id}:role:instructor",
                f"cg:{context.id}:role:moderator",
            ],
            list(
                Group.objects.filter(name__startswith=f"cg:{context.id}")
                .order_by("name")
                .values_list("name", flat=True)
            ),
        )
