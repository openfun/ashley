"""Test suite for ashley custom tags"""
import logging
from typing import List

from django.template import Context, Template
from django.test import TestCase
from django.test.html import parse_html
from django.urls import reverse
from lxml import etree
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.loading import get_class
from with_asserts.mixin import AssertHTMLMixin

from ashley.defaults import (
    DEFAULT_FORUM_BASE_PERMISSIONS,
    DEFAULT_FORUM_ROLES_PERMISSIONS,
)
from ashley.factories import (
    ForumFactory,
    LTIConsumerFactory,
    LTIContextFactory,
    PostFactory,
    TopicFactory,
    UserFactory,
)

get_forum_member_display_name = get_class(
    "forum_member.shortcuts", "get_forum_member_display_name"
)

logger = logging.getLogger(__name__)


class TestIsUserInstructorTag(TestCase, AssertHTMLMixin):
    """
    Integration tests to validate that the filter is_user_instructor
    can detect if user is instructor of a forum
    """

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

    @staticmethod
    def test_can_tell_if_the_user_is_instructor_of_this_forum():
        """
        Given two users. User1 is student of the forum, User2 is instructor.
        We control that is_user_instructor can detect if a user is an instructor.
        Then a forum can be part of multiple contexts. If a user is instructor in one context,
        he is considered admin of this forum in all contexts. We add a new context to the forum
        where user is instructor and test that user is now considered as instructor
        """
        # load template
        def get_rendered(topic, user):
            template = Template(
                "{% load custom_tags %}"
                + "{% if topic|is_user_instructor:user %}YES{% else %}NO{% endif %}"
            )
            context = Context({"topic": topic, "user": user})
            rendered = template.render(context)

            return rendered

        lti_consumer = LTIConsumerFactory()
        # Create two LTI Context
        context1 = LTIContextFactory(lti_consumer=lti_consumer)
        context2 = LTIContextFactory(lti_consumer=lti_consumer)
        # Create two users
        user1 = UserFactory(lti_consumer=lti_consumer)
        user2 = UserFactory(lti_consumer=lti_consumer)

        # Sync user1 groups in context1 with role "student"
        context1.sync_user_groups(user1, ["student"])
        # Sync user1 groups in context2 with role "instructor"
        context2.sync_user_groups(user1, ["instructor"])
        # Sync user2 groups in context1 with role "instructor"
        context1.sync_user_groups(user2, ["instructor"])

        # Create forum and add context1
        forum = ForumFactory(name="Initial forum name")
        forum.lti_contexts.add(context1)

        # Set up topic
        topic = TopicFactory(forum=forum, poster=user1, subject="topic création")

        # Chek that user1 is not instructor
        assert get_rendered(topic, user1) == "NO"
        # Chek that user2 is instructor
        assert get_rendered(topic, user2) == "YES"

        # Add forum to context2 where user1 has role "instructor"
        forum.lti_contexts.add(context2)
        # Check that user1 is now instructor as well
        assert get_rendered(topic, user1) == "YES"

    def test_render_block_is_instructor_of_this_forum(self):
        """
        check that the instructor icon is present on the different views
        as expected
        """
        lti_consumer = LTIConsumerFactory()
        # Create two users
        user1 = UserFactory(public_username="Valéry", lti_consumer=lti_consumer)
        user2 = UserFactory(public_username="François", lti_consumer=lti_consumer)
        # Create an LTI Context
        context = LTIContextFactory(lti_consumer=lti_consumer)
        # Sync user1 groups in context with role "instructor"
        context.sync_user_groups(user1, ["instructor"])
        # Sync user1 groups in context with role "student"
        context.sync_user_groups(user2, ["student"])

        # Create forum and add context
        forum = ForumFactory(name="forum_test")
        forum.lti_contexts.add(context)

        # assign permission to the group for this forum
        self._init_forum(forum, context)

        # Set up topic
        topic1 = TopicFactory(forum=forum, poster=user1)

        # Set up post
        PostFactory.create(
            topic=topic1,
            poster=user1,
        )

        # log user1
        self.client.force_login(user1)

        # accessing forum view
        response = self.client.get(reverse("forum:index"))
        with self.assertHTML(response, ".forum-last-post") as (html,):
            fragment = parse_html(str(etree.tostring(html)))
            # control that the instructor's icon is present
            self.assertTrue(
                parse_html(
                    '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                    '<span class="sr-only">Instructor</span>'
                    "</i>"
                )
                in fragment
            )
            # control that it's the right user's profil link
            self.assertTrue(
                parse_html(f'<a href="/forum/member/profile/{user1.id}/">Valéry</a>')
                in fragment
            )

        # accessing forum topic listing view
        response = self.client.get(
            reverse("forum:forum", kwargs={"slug": forum.slug, "pk": forum.pk})
        )
        # check that the topic creation writer contains the icon for instructor's role
        with self.assertHTML(response, ".topic-created") as (html,):
            fragment = parse_html(str(etree.tostring(html)))
            # control that the instructor's icon is present
            self.assertTrue(
                parse_html(
                    '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                    '<span class="sr-only">Instructor</span>'
                    "</i>"
                )
                in fragment
            )
            # control that it's the right user's profil link
            self.assertTrue(
                parse_html(f'<a href="/forum/member/profile/{user1.id}/">Valéry</a>')
                in fragment
            )

        # check that the last post creation writer contains the icon for instructor's role
        with self.assertHTML(response, ".topic-last-post") as (html,):
            fragment = parse_html(str(etree.tostring(html)))
            # control that the instructor's icon is present
            self.assertTrue(
                parse_html(
                    '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                    '<span class="sr-only">Instructor</span>'
                    "</i>"
                )
                in fragment
            )
            # control that it's the right user's profil link
            self.assertTrue(
                parse_html(f'<a href="/forum/member/profile/{user1.id}/">Valéry</a>')
                in fragment
            )

        # user2 add a post to the topic, last message is now from a student
        PostFactory.create(
            topic=topic1,
            poster=user2,
        )

        # reload the topic list view
        response = self.client.get(
            reverse("forum:forum", kwargs={"slug": forum.slug, "pk": forum.pk})
        )

        with self.assertHTML(response, ".topic-created") as (html,):
            fragment = parse_html(str(etree.tostring(html)))
            # control that the instructor's icon is present
            self.assertTrue(
                parse_html(
                    '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                    '<span class="sr-only">Instructor</span>'
                    "</i>"
                )
                in fragment
            )
            # control that it's the right profil link
            self.assertTrue(
                parse_html(f'<a href="/forum/member/profile/{user1.id}/">Valéry</a>')
                in fragment
            )

        # check that the last post creation writer is not the previous one with the icon
        with self.assertHTML(response, ".topic-last-post") as (html,):
            fragment = parse_html(str(etree.tostring(html)))
            # check that there's no more icon as the post has been created by a student
            self.assertFalse(parse_html("Instructor") in fragment)

            # control that it's the right profil link
            self.assertTrue(
                parse_html(f'<a href="/forum/member/profile/{user2.id}/">François</a>')
                in fragment
            )

        # accessing forum view
        response = self.client.get(reverse("forum:index"))
        # check that there's no more icon in this view as a new post has been created by a student
        self.assertNotContains(response, "icon_writer fas fa-award")

        # access list of posts from the topic
        response = self.client.get(
            reverse(
                "forum_conversation:topic",
                kwargs={
                    "forum_slug": forum.slug,
                    "forum_pk": forum.pk,
                    "slug": topic1.slug,
                    "pk": topic1.id,
                },
            )
        )
        # access 'post an answer' it should list the other posts of the topic
        response = self.client.get(
            f"/forum/forum/{forum.slug}-{forum.pk}/topic/{topic1.slug}-{topic1.pk}/post/create/"
        )
        # check that for the posts in this topic we have the one from the instructor with the icon
        with self.assertHTML(response, ".text-muted") as (
            first_post,
            second_post,
        ):
            # check that for the message on first position there is no icon for the student
            html_first_post = parse_html(str(etree.tostring(first_post)))
            self.assertFalse(parse_html("Instructor") in html_first_post)
            self.assertTrue(
                parse_html(f'<a href="/forum/member/profile/{user2.id}/">François</a>')
                in html_first_post
            )
            # check that for the second message we have the instructor's icon
            html_second_post = parse_html(str(etree.tostring(second_post)))
            self.assertTrue(
                parse_html(
                    '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                    '<span class="sr-only">Instructor</span>'
                    "</i>"
                )
                in html_second_post
            )
            self.assertTrue(
                parse_html(f'<a href="/forum/member/profile/{user1.id}/">Valéry</a>')
                in html_second_post
            )
