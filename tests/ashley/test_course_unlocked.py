"""Test suite for ashley ForumUnlockCourseView."""
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.test import TestCase
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from machina.apps.forum_permission.shortcuts import remove_perm
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

from ashley.factories import ForumFactory, PostFactory, TopicFactory

from tests.ashley.lti_utils import CONTENT_TYPE, sign_parameters

Forum = get_model("forum", "Forum")
LTIContext = get_model("ashley", "LTIContext")
PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)
User = get_user_model()
GroupForumPermission = get_model("forum_permission", "GroupForumPermission")


class CourseUnlockCase(TestCase):
    """Test the CourseUnlockCase class"""

    forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
    context_id = "course-v1:testschool+login+0001"

    def _connects(
        self,
        role,
        forum_uuid=None,
        uuid="643f1625-f240-4a5a-b6eb-89b317807963",
        lis_person_sourcedid="testuser",
    ):
        """
        Utils not to repeat the connection of an instructor or
        a student
        """
        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        forum_uuid = forum_uuid or self.forum_uuid

        # Build the LTI launch request
        lti_parameters = {
            "user_id": uuid,
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": self.context_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": lis_person_sourcedid,
            "launch_presentation_locale": "en",
            "roles": role.capitalize(),
        }

        url = f"http://testserver/lti/forum/{forum_uuid}"
        signed_parameters = sign_parameters(passport, lti_parameters, url)

        self.client.post(
            f"/lti/forum/{forum_uuid}",
            data=urlencode(signed_parameters),
            content_type=CONTENT_TYPE,
        )

        forum = Forum.objects.get(
            lti_id=forum_uuid,
            lti_contexts__id=LTIContext.objects.get(
                lti_id=self.context_id, lti_consumer_id=passport.consumer
            ).id,
        )

        return forum

    def test_course_info_course_student_cant_unlock(self):
        """
        User is a student, he shouldn't see the CTA to unlock the course
        and he can't unlock a course using the url.
        As a student he can create new topic or new post.
        """
        forum = self._connects("student")

        # A LTIContext and a Forum should have been created
        post = PostFactory(topic=TopicFactory(forum=forum))

        url = f"/forum/forum/{forum.slug}-{forum.pk}/"
        response = self.client.get(url)
        url_topic_create = f"{url}topic/create/"
        # user is a student and he can create a new topic
        self.assertContains(
            response,
            f'<a href="{url_topic_create}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comments fa-lg"></i>&nbsp;New topic</a>',
            html=True,
        )
        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(200, response.status_code)

        # user has no button to unlock the course
        self.assertNotContains(response, "Unlock forums")

        # user can answer a post
        url_topic = f"{url}topic/{post.topic.slug}-{post.topic.pk}/"
        response = self.client.get(url_topic, follow=True)
        url_topic_reply = f"{url_topic}post/create/"
        self.assertContains(
            response,
            f'<a href="{url_topic_reply}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comment fa-lg"></i>&nbsp;Post reply</a>',
            html=True,
        )
        response = self.client.get(url_topic_reply, follow=True)
        self.assertEqual(200, response.status_code)

        # user can't access the view to unlock the course
        response = self.client.get(f"/forum/admin/unlock-course/{forum.id}/")
        self.assertEqual(403, response.status_code)

        # user can't post to activate the unlock on the course
        response = self.client.post(f"/forum/admin/unlock-course/{forum.id}/")
        self.assertEqual(403, response.status_code)

    def test_course_info_course_instructor_can_unlock(self):
        """
        User is an instructor or an administrator, it should see the CTA
        to unlock the course and he can unlock the course.
        Once the course is unlocked, permissions of created groups have changed.
        """
        forum = self._connects("instructor")
        # A LTIContext and a Forum should have been created
        context = LTIContext.objects.get(lti_id=self.context_id)

        # create a post in the forum
        PostFactory(topic=TopicFactory(forum=forum))

        # focus on permission of groups created
        base_group = context.get_base_group()
        instructor_group = context.get_role_group("instructor")

        count_perm_instructor = GroupForumPermission.objects.filter(
            forum=forum, group=instructor_group, has_perm=True
        ).count()
        count_perm_base = GroupForumPermission.objects.filter(
            forum=forum, group=base_group, has_perm=True
        ).count()

        self.assertEqual(
            [
                "can_see_forum",
                "can_read_forum",
                "can_start_new_topics",
                "can_reply_to_topics",
                "can_edit_own_posts",
                "can_post_without_approval",
                "can_vote_in_polls",
            ],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=base_group, has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )
        url_forum = f"/forum/forum/{forum.slug}-{forum.pk}/"
        url_unlock = f"/forum/admin/unlock-course/{forum.id}/"
        response = self.client.get(url_forum)
        self.assertEqual(context.is_marked_locked, False)

        # lock the forum
        response = self.client.post(
            f"/forum/admin/lock-course/{forum.id}/", follow=True
        )
        self.assertEqual(200, response.status_code)

        # course is now marked as locked
        context.refresh_from_db()
        self.assertEqual(context.is_marked_locked, True)

        # permissions of instructor haven't changed
        self.assertEqual(
            count_perm_instructor,
            GroupForumPermission.objects.filter(
                forum=forum, group=instructor_group, has_perm=True
            ).count(),
        )

        # for base group, five permissions have been deleted
        self.assertEqual(
            count_perm_base - 5,
            GroupForumPermission.objects.filter(
                forum=forum, group=base_group, has_perm=True
            ).count(),
        )

        # user can now access the view to unlock a course
        response = self.client.get(url_unlock)
        self.assertEqual(200, response.status_code)

        # user can post to activate the unlock on the course
        response = self.client.post(url_unlock, follow=True)
        self.assertEqual(200, response.status_code)

        # course is now marked as unlocked
        context.refresh_from_db()
        self.assertEqual(context.is_marked_locked, False)

        response = self.client.get(url_forum)

        # the cta to lock is no more present as forum is already locked
        self.assertNotContains(
            response,
            "Unlock forums",
            html=True,
        )
        # the cta to lock is now present
        self.assertContains(
            response,
            f'<a href="/forum/admin/lock-course/{forum.id}/" title="Lock forums" '
            'class="dropdown-item">Lock forums</a>',
            html=True,
        )

        # permissions of instructor haven't changed
        self.assertEqual(
            count_perm_instructor,
            GroupForumPermission.objects.filter(
                forum=forum, group=instructor_group, has_perm=True
            ).count(),
        )

        # for base group, original permissions have been reset
        self.assertEqual(
            count_perm_base,
            GroupForumPermission.objects.filter(
                forum=forum, group=base_group, has_perm=True
            ).count(),
        )

    def test_course_student_course_unlocked_student_connects_before(self):
        """
        We create a student before and then an instructor that locks the course.
        Student connects on the course being locked.
        Then the instructor unlocks the course. The students reconnects, the course
        should now be unlocked. This control that users that have been logged during
        a forum locked can still use the forum once it has been unlocked
        """
        user_count = 0
        forum = self._connects("student")
        # one user has been created
        self.assertEqual(user_count + 1, User.objects.count())
        user_count += 1
        user = User.objects.last()

        # create a post in the forum
        post = PostFactory(topic=TopicFactory(forum=forum, poster=user), poster=user)
        # context object has been created
        context = LTIContext.objects.get(lti_id=self.context_id)

        student_group = context.get_role_group("student")
        base_group = context.get_base_group()
        # student group contains no permission, all permissions are in the
        # base group
        self.assertEqual(
            [],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=student_group, has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        # check base group permission
        count_perm_base = GroupForumPermission.objects.filter(
            forum=forum, group=base_group, has_perm=True
        ).count()

        self.assertEqual(
            [
                "can_see_forum",
                "can_read_forum",
                "can_start_new_topics",
                "can_reply_to_topics",
                "can_edit_own_posts",
                "can_post_without_approval",
                "can_vote_in_polls",
            ],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=base_group, has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        self._connects("instructor", uuid="NewOne", lis_person_sourcedid="enzo")

        # admin user has been created
        self.assertEqual(user_count + 1, User.objects.count())
        user_count += 1

        # lock the course
        response = self.client.post(
            f"/forum/admin/lock-course/{forum.id}/", follow=True
        )
        self.assertEqual(200, response.status_code)
        # permissions of the base group have been deleted
        self.assertEqual(
            count_perm_base - 5,
            GroupForumPermission.objects.filter(
                forum=forum, group=base_group, has_perm=True
            ).count(),
        )
        url_forum = f"/forum/forum/{forum.slug}-{forum.pk}/"
        response = self.client.get(url_forum)
        url_topic_create = f"{url_forum}topic/create/"
        # instructor can see creating topics
        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(200, response.status_code)

        # reconnect the student user
        self._connects("student")
        # no new user has been created
        self.assertEqual(user_count, User.objects.count())

        # can't create the topic as the forum is locked
        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(403, response.status_code)

        # reconnect instructor
        self._connects("instructor", uuid="NewOne", lis_person_sourcedid="enzo")
        # no new user has been created
        self.assertEqual(user_count, User.objects.count())

        # unlock the course
        url_unlock = f"/forum/admin/unlock-course/{forum.id}/"
        response = self.client.post(url_unlock, follow=True)
        self.assertEqual(200, response.status_code)

        # course is now marked as unlocked
        context.refresh_from_db()
        self.assertEqual(context.is_marked_locked, False)
        # permissions of the base group have been reset
        self.assertEqual(
            count_perm_base,
            GroupForumPermission.objects.filter(
                forum=forum, group=base_group, has_perm=True
            ).count(),
        )

        # reconnect the student user
        self._connects("student")
        # no new user has been created
        self.assertEqual(user_count, User.objects.count())

        # user can create a topic
        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(200, response.status_code)

        # user can answer a post
        url_topic_reply = (
            f"{url_forum}topic/{post.topic.slug}-{post.topic.pk}/post/create/"
        )
        response = self.client.get(url_topic_reply, follow=True)
        self.assertEqual(200, response.status_code)

    def test_course_unlock_already_locked(self):
        """
        A course that is not locked can't be unlocked
        """
        forum = self._connects("instructor")
        # create a post in the forum
        PostFactory(topic=TopicFactory(forum=forum))
        # context object has been created
        context = LTIContext.objects.get(lti_id=self.context_id)
        self.assertEqual(context.is_marked_locked, False)

        # course is already unlocked
        response = self.client.post(
            f"/forum/admin/unlock-course/{forum.id}/", follow=True
        )
        self.assertEqual(403, response.status_code)

    def test_course_create_multiple_forums_listing_on(self):
        """
        Instructor wants to unlock the course that has multiple forums.
        The list of forums should be displayed before the confirmation's
        button.
        """
        forum1 = self._connects("instructor")
        forum2 = ForumFactory(name="Forum2")
        forum3 = ForumFactory(name="Forum3")
        # connects user and add forums to the lti_context
        forum2 = self._connects("instructor", forum_uuid=forum2.lti_id)
        forum3 = self._connects("instructor", forum_uuid=forum3.lti_id)

        # lock the course
        response = self.client.post(
            f"/forum/admin/lock-course/{forum1.id}/", follow=True
        )
        self.assertEqual(200, response.status_code)
        # go on the unlock page
        response = self.client.get(
            f"/forum/admin/lock-course/{forum1.id}/", follow=True
        )
        self.assertEqual(200, response.status_code)
        # this listing is common for all the forums of the course
        forums_list = (
            f'<p class="ml-3 mb-0"><strong>{forum1.name}</strong></p>'
            '<p class="ml-3 mb-0"><strong>Forum2</strong></p>'
            '<p class="ml-3 mb-0"><strong>Forum3</strong></p>'
        )
        self.assertContains(response, forums_list)

        # go on the page to unlock the course from the forum2
        response = self.client.get(f"/forum/admin/unlock-course/{forum2.id}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, forums_list)

        # go on the page to unlock the course from the forum3
        response = self.client.get(f"/forum/admin/unlock-course/{forum3.id}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, forums_list)

    def test_is_marked_unlocked_set_in_the_back(self):
        """
        Check when the tag is_marked_locked is set to False out of a web navigation
        that the forum gets unblocked anyway
        """
        forum = self._connects("instructor")
        context = LTIContext.objects.get(lti_id=self.context_id)

        url_lock = f"/forum/admin/lock-course/{forum.id}/"
        response = self.client.post(url_lock, follow=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_base_group(), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        # first lock the course
        forum = self._connects("instructor")
        # course is now marked as locked
        context.refresh_from_db()
        self.assertEqual(context.is_marked_locked, True)

        # change field is_marked_locked to False
        context.is_marked_locked = False
        context.save()
        self.assertEqual(context.is_marked_locked, False)

        # connects the student
        self._connects("student", uuid="NewOne", lis_person_sourcedid="enzo")

        # standard group gets the right permissions
        self.assertEqual(
            [
                "can_see_forum",
                "can_read_forum",
                "can_start_new_topics",
                "can_reply_to_topics",
                "can_edit_own_posts",
                "can_post_without_approval",
                "can_vote_in_polls",
            ],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_base_group(), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

    def test_is_marked_unlocked_and_some_writing_perm(self):
        """
        Check when the tag is_marked_locked is set to False and that
        there are some missing writing permissions for the base group,
        that synchronization is still played when user is connecting
        """
        forum = self._connects("instructor")
        context = LTIContext.objects.get(lti_id=self.context_id)
        base_group = context.get_base_group()
        # change field is_marked_locked to False
        context.is_marked_locked = False
        context.save()
        # remove some writing permissions
        remove_perm("can_start_new_topics", base_group, forum)
        remove_perm("can_edit_own_posts", base_group, forum)
        remove_perm("can_post_without_approval", base_group, forum)
        remove_perm("can_vote_in_polls", base_group, forum)
        self.assertEqual(context.is_marked_locked, False)
        context.refresh_from_db()
        self.assertEqual(
            [
                "can_see_forum",
                "can_read_forum",
                "can_reply_to_topics",
            ],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=base_group, has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        # connects the student
        self._connects("student", uuid="NewOne", lis_person_sourcedid="enzo")

        # permissions gets added
        self.assertEqual(
            [
                "can_see_forum",
                "can_read_forum",
                "can_reply_to_topics",
                "can_start_new_topics",
                "can_edit_own_posts",
                "can_post_without_approval",
                "can_vote_in_polls",
            ],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=base_group, has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )
