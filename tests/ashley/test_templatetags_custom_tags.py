"""Test suite for ashley custom tags"""
import logging
from typing import List

import lxml.html  # nosec
from django.template import Context, Template
from django.test import TestCase
from django.urls import reverse
from lxml import etree  # nosec
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.loading import get_class

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

# pylint: disable = C0209, W0232, c-extension-no-member


class TestIsUserInstructorTag(TestCase):
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
        he is considered intructor of this forum in all contexts. We add a new context to the forum
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
        html = lxml.html.fromstring(response.content)
        forum_last_post = str(etree.tostring(html.cssselect(".forum-last-post")[0]))
        # control that the instructor's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                '<span class="sr-only">Instructor</span>'
                "</i>"
            )
            in forum_last_post
        )
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in forum_last_post
        )

        # accessing forum topic listing view
        response = self.client.get(
            reverse("forum:forum", kwargs={"slug": forum.slug, "pk": forum.pk})
        )
        html = lxml.html.fromstring(response.content)
        # check that the topic creation writer contains the icon for instructor's role
        topic_created = str(etree.tostring(html.cssselect(".topic-created")[0]))
        # control that the instructor's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                '<span class="sr-only">Instructor</span>'
                "</i>"
            )
            in topic_created
        )
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in topic_created
        )

        # check that the last post creation writer contains the icon for instructor's role
        html = lxml.html.fromstring(response.content)
        topic_last_post = str(etree.tostring(html.cssselect(".topic-last-post")[0]))
        # control that the instructor's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                '<span class="sr-only">Instructor</span>'
                "</i>"
            )
            in topic_last_post
        )
        # control that it's the right user's profile link
        self.assertTrue(
            f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>'
            in topic_last_post
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
        html = lxml.html.fromstring(response.content)
        topic_created = str(etree.tostring(html.cssselect(".topic-created")[0]))
        # control that the instructor's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                '<span class="sr-only">Instructor</span>'
                "</i>"
            )
            in topic_created
        )
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in topic_created
        )

        topic_last_post = str(etree.tostring(html.cssselect(".topic-last-post")[0]))
        # check that there's no more icon as the post has been created by a student
        self.assertFalse("Instructor" in topic_last_post)
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user2.id}/">Fran&#231;ois</a>')
            in topic_last_post
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
        html = lxml.html.fromstring(response.content)
        # check that for the posts in this topic we have the one from the instructor with the icon

        # check that for the message on first position there is no icon for the student
        html_first_post = str(etree.tostring(html.cssselect(".text-muted")[0]))
        self.assertFalse("Instructor" in html_first_post)
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user2.id}/">Fran&#231;ois</a>')
            in html_first_post
        )
        # check that for the second message we have the instructor's icon
        html_second_post = str(etree.tostring(html.cssselect(".text-muted")[1]))
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Instructor">'
                '<span class="sr-only">Instructor</span>'
                "</i>"
            )
            in html_second_post
        )
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in html_second_post
        )

    @staticmethod
    def test_can_tell_if_the_user_is_administrator_of_this_forum():
        """
        Given two users. User1 is student of the forum, User2 is administrator.
        We control that is_user_administrator can detect if a user is an administrator.
        Then a forum can be part of multiple contexts. If a user is administrator in one context,
        he is considered intructor of this forum in all contexts. We add a new context to the forum
        where user is administrator and test that user is now considered as administrator
        """
        # load template
        def get_rendered(topic, user):
            template = Template(
                "{% load custom_tags %}"
                + "{% if topic|is_user_administrator:user %}YES{% else %}NO{% endif %}"
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
        # Sync user1 groups in context2 with role "administrator"
        context2.sync_user_groups(user1, ["administrator"])
        # Sync user2 groups in context1 with role "administrator"
        context1.sync_user_groups(user2, ["administrator"])

        # Create forum and add context1
        forum = ForumFactory(name="Initial forum name")
        forum.lti_contexts.add(context1)

        # Set up topic
        topic = TopicFactory(forum=forum, poster=user1, subject="topic création")

        # Chek that user1 is not administrator
        assert get_rendered(topic, user1) == "NO"
        # Chek that user2 is administrator
        assert get_rendered(topic, user2) == "YES"

        # Add forum to context2 where user1 has role "administrator"
        forum.lti_contexts.add(context2)
        # Check that user1 is now administrator as well
        assert get_rendered(topic, user1) == "YES"

    def test_render_block_is_admin_of_this_forum(self):
        """
        check that the admin icon is present on the different views
        as expected
        """
        lti_consumer = LTIConsumerFactory()
        # Create two users
        user1 = UserFactory(public_username="Valéry", lti_consumer=lti_consumer)
        user2 = UserFactory(public_username="François", lti_consumer=lti_consumer)
        # Create an LTI Context
        context = LTIContextFactory(lti_consumer=lti_consumer)
        # Sync user1 groups in context with role "administrator"
        context.sync_user_groups(user1, ["administrator"])
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
        html = lxml.html.fromstring(response.content)
        forum_last_post = str(etree.tostring(html.cssselect(".forum-last-post")[0]))
        # control that the administrator's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Administrator">'
                '<span class="sr-only">Administrator</span>'
                "</i>"
            )
            in forum_last_post
        )
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in forum_last_post
        )

        # accessing forum topic listing view
        response = self.client.get(
            reverse("forum:forum", kwargs={"slug": forum.slug, "pk": forum.pk})
        )
        html = lxml.html.fromstring(response.content)
        # check that the topic creation writer contains the icon for administrator's role
        topic_created = str(etree.tostring(html.cssselect(".topic-created")[0]))
        # control that the administrator's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Administrator">'
                '<span class="sr-only">Administrator</span>'
                "</i>"
            )
            in topic_created
        )
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in topic_created
        )

        # check that the last post creation writer contains the icon for instructor's role
        html = lxml.html.fromstring(response.content)
        topic_last_post = str(etree.tostring(html.cssselect(".topic-last-post")[0]))
        # control that the administrator's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Administrator">'
                '<span class="sr-only">Administrator</span>'
                "</i>"
            )
            in topic_last_post
        )
        # control that it's the right user's profile link
        self.assertTrue(
            f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>'
            in topic_last_post
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
        html = lxml.html.fromstring(response.content)
        topic_created = str(etree.tostring(html.cssselect(".topic-created")[0]))
        # control that the administrator's icon is present
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Administrator">'
                '<span class="sr-only">Administrator</span>'
                "</i>"
            )
            in topic_created
        )
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in topic_created
        )

        topic_last_post = str(etree.tostring(html.cssselect(".topic-last-post")[0]))
        # check that there's no more icon as the post has been created by a student
        self.assertFalse("Administrator" in topic_last_post)
        # control that it's the right user's profile link
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user2.id}/">Fran&#231;ois</a>')
            in topic_last_post
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
        html = lxml.html.fromstring(response.content)
        # check that for the posts in this topic we have the one from the instructor with the icon

        # check that for the message on first position there is no icon for the student
        html_first_post = str(etree.tostring(html.cssselect(".text-muted")[0]))
        self.assertFalse("Administrator" in html_first_post)
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user2.id}/">Fran&#231;ois</a>')
            in html_first_post
        )
        # check that for the second message we have the instructor's icon
        html_second_post = str(etree.tostring(html.cssselect(".text-muted")[1]))
        self.assertTrue(
            (
                '<i class="icon_writer fas fa-award" aria-hidden="true" title="Administrator">'
                '<span class="sr-only">Administrator</span>'
                "</i>"
            )
            in html_second_post
        )
        self.assertTrue(
            (f'<a href="/forum/member/profile/{user1.id}/">Val&#233;ry</a>')
            in html_second_post
        )
