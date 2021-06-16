from typing import List

from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.defaults import (
    DEFAULT_FORUM_BASE_PERMISSIONS,
    DEFAULT_FORUM_ROLES_PERMISSIONS,
)
from ashley.factories import (
    ForumFactory,
    LTIContextFactory,
    PostFactory,
    TopicFactory,
    UserFactory,
)
from ashley.machina_extensions.forum_moderation.forms import TopicMoveForm


class ForumModerationTestViewForm(TestCase):
    def _init_forum(self, forum, context):
        """
        Initialize a forum.

        This method sets default permissions according to the LTI context that
        initiated the creation of the forum.
        """
        forum.lti_contexts.add(context)
        self._assign_permissions(
            forum,
            context.get_base_group(),
            DEFAULT_FORUM_BASE_PERMISSIONS,
        )
        # pylint: disable=no-member
        for role, perms in DEFAULT_FORUM_ROLES_PERMISSIONS.items():
            self._assign_permissions(forum, context.get_role_group(role), perms)

    @staticmethod
    def _assign_permissions(forum, group, permissions: List[str]):
        """Grant a list of permissions for a group on a specific forum."""
        for perm in permissions:
            assign_perm(perm, group, forum, True)

    def test_forum_moderation_list_forums_view(self):
        """
        Create forum in different LTIContext, make sure user can't move topics into it,
        even if he has access to this forum.
        """
        user = UserFactory()

        lti_context1 = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context2 = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum1Lti1 = ForumFactory(name="Forum1")
        forum2Lti1 = ForumFactory(name="Forum2")
        forum3Lti2 = ForumFactory(name="Forum3")
        forum4Lti2 = ForumFactory(name="Forum4")

        # User is instructor in both forums
        lti_context1.sync_user_groups(user, ["instructor"])
        lti_context2.sync_user_groups(user, ["instructor"])

        # Assign permission to the group for this forum
        self._init_forum(forum1Lti1, lti_context1)
        self._init_forum(forum2Lti1, lti_context1)
        self._init_forum(forum3Lti2, lti_context2)
        self._init_forum(forum4Lti2, lti_context2)

        # Create a post for a topic part of lti_context1
        topicForumLti1 = TopicFactory(forum=forum1Lti1)
        PostFactory(
            topic=topicForumLti1,
        )

        # Create a post for a topic part of lti_context2
        topicForumLti2 = TopicFactory(forum=forum3Lti2)
        PostFactory(
            topic=topicForumLti2,
        )

        # Create the session and log in lti_context1
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context1.id
        session.save()

        # Requests url to move the topic
        response = self.client.get(
            f"/forum/moderation/topic/{topicForumLti1.slug}-{topicForumLti1.id}/move/"
        )
        # Checks we are on the right page
        self.assertContains(response, "Move topic", html=True)

        # Forum2 part of lti_context1 should be proposed not the others
        self.assertContains(response, forum2Lti1.name)
        self.assertNotContains(response, forum3Lti2.name)
        self.assertNotContains(response, forum4Lti2.name)

        # Change the session to connect user to lti_context2
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context2.id
        session.save()

        # Forum4 part of lti_context2 should be proposed not the others
        response = self.client.get(
            f"/forum/moderation/topic/{topicForumLti2.slug}-{topicForumLti2.id}/move/"
        )
        self.assertContains(response, forum4Lti2.name)
        self.assertNotContains(response, forum2Lti1.name)
        self.assertNotContains(response, forum1Lti1.name)

    def test_forum_moderation_list_forums_form(self):
        """
        Create forum in different LTIContext. Load the form to choose to which forum
        user wants to move the topic. Try to move it to a forum that is not allowed and
        control that it's not possible.
        """
        user = UserFactory()

        lti_context1 = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context2 = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum1Lti1 = ForumFactory(name="Forum1")
        forum2Lti1 = ForumFactory(name="Forum2")
        forum3Lti2 = ForumFactory(name="Forum3")

        # User is instructor in both forums
        lti_context1.sync_user_groups(user, ["instructor"])
        lti_context2.sync_user_groups(user, ["instructor"])

        # Assign permission to the group for this forum
        self._init_forum(forum1Lti1, lti_context1)
        self._init_forum(forum2Lti1, lti_context1)
        self._init_forum(forum3Lti2, lti_context2)

        # Create a post for a topic part of lti_context1
        topicForumLti1 = TopicFactory(forum=forum1Lti1)
        PostFactory(
            topic=topicForumLti1,
        )

        # Create the session and logged in lti_context1
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context1.id
        session.save()

        form = TopicMoveForm(user=user, lti_context=lti_context1, topic=topicForumLti1)

        # Check that only the forum that is allowed is proposed as choice
        self.assertEqual(
            form.fields["forum"].choices,
            [
                (forum1Lti1.id, {"label": " Forum1", "disabled": True}),
                (
                    forum2Lti1.id,
                    "{} {}".format("-" * forum2Lti1.margin_level, forum2Lti1.name),
                ),
            ],
        )

        # We move the forum to topic2 part of the same lti_context1
        response = self.client.post(
            f"/forum/moderation/topic/{topicForumLti1.slug}-{topicForumLti1.id}/move/",
            data={"forum": {forum2Lti1.id}},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This topic has been moved successfully.")

        # We force the request on the forum that is not allowed
        response = self.client.post(
            f"/forum/moderation/topic/{topicForumLti1.slug}-{topicForumLti1.id}/move/",
            data={"forum": {forum3Lti2.id}},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)

        # Controls that we get an error and the move is not executed
        self.assertContains(
            response,
            f"Select a valid choice. {forum3Lti2.id} is not one of the available choices.",
            html=True,
        )
