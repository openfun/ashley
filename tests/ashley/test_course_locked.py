"""Test suite for ashley ForumLTIView."""
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from lti_toolbox.factories import LTIConsumerFactory, LTIPassportFactory
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

from ashley.factories import ForumFactory, PostFactory, TopicFactory, UserFactory

from tests.ashley.lti_utils import CONTENT_TYPE, sign_parameters

Forum = get_model("forum", "Forum")
LTIContext = get_model("ashley", "LTIContext")
PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)
User = get_user_model()
GroupForumPermission = get_model("forum_permission", "GroupForumPermission")


class CourseLockCase(TestCase):
    """Test the CourseLockCase class"""

    forum_uuid = "8bb319aa-f3cf-4509-952c-c4bd0fb42fd7"
    context_id = "course-v1:testschool+login+0001"

    def _connects(self, role, forum_uuid=None, uuid=None, lis_person_sourcedid=None):
        """
        Utils not to repeat the connection of an instructor or
        a student
        """
        consumer = LTIConsumerFactory(slug="consumer")
        passport = LTIPassportFactory(title="consumer1_passport1", consumer=consumer)

        if not forum_uuid:
            forum_uuid = self.forum_uuid

        # Build the LTI launch request
        lti_parameters = {
            "user_id": "643f1625-f240-4a5a-b6eb-89b317807963" if not uuid else uuid,
            "lti_message_type": "basic-lti-launch-request",
            "lti_version": "LTI-1p0",
            "resource_link_id": "aaa",
            "context_id": self.context_id,
            "lis_person_contact_email_primary": "ashley@example.com",
            "lis_person_sourcedid": "testuser"
            if not lis_person_sourcedid
            else lis_person_sourcedid,
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

    def test_course_info_course_student_cant_locked(self):
        """
        User is a student, he shouldn't see the CTA to lock the course
        and he can't lock a course using the url.
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

        # user has no button to lock the course
        self.assertNotContains(response, "Lock forums")

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

        # user can't access the view to lock the course
        response = self.client.get(f"/forum/admin/lock-course/{forum.id}/")
        self.assertEqual(403, response.status_code)

        # user can't post to activate the lock on the course
        response = self.client.post(f"/forum/admin/lock-course/{forum.id}/")
        self.assertEqual(403, response.status_code)

    def test_course_info_course_instructor_can_locked(self):
        """
        User is an instructor or an administrator, it should see the CTA
        to lock the course and he can lock the course.
        Once the course is locked, permissions of created groups have changed
        and information of the course being locked is displayed.
        """
        forum = self._connects("instructor")
        # A LTIContext and a Forum should have been created
        context = LTIContext.objects.get(lti_id=self.context_id)
        self.assertEqual(context.is_marked_locked, False)

        # create a post in the forum
        post = PostFactory(topic=TopicFactory(forum=forum))

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
        url_lock = f"/forum/admin/lock-course/{forum.id}/"
        response = self.client.get(url_forum)
        self.assertContains(
            response,
            f'<a href="{url_lock}" title="Lock forums" class="dropdown-item">Lock forums</a>',
            html=True,
        )

        # user can access the view to lock a course
        response = self.client.get(url_lock)
        self.assertEqual(200, response.status_code)

        # user can't post to activate the lock on the course
        response = self.client.post(url_lock, follow=True)
        self.assertEqual(200, response.status_code)

        # course is now marked as locked
        context.refresh_from_db()
        self.assertEqual(context.is_marked_locked, True)

        # info is present in forums view
        response = self.client.get("/forum/")
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        # info is present in the forum view
        url_forum = f"/forum/forum/{forum.slug}-{forum.pk}/"
        response = self.client.get(url_forum)
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        # the cta to lock is no more present as forum is already locked
        self.assertNotContains(
            response,
            f'<a href="{url_lock}" title="Lock forums" class="dropdown-item">Lock forums</a>',
            html=True,
        )

        # info is present in topic view
        response = self.client.get(
            f"{url_forum}topic/{post.topic.slug}-{post.topic.pk}/"
        )
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )

        # permissions of instructor haven't changed
        self.assertEqual(
            count_perm_instructor,
            GroupForumPermission.objects.filter(
                forum=forum, group=instructor_group, has_perm=True
            ).count(),
        )

        # for base group, five permissions should have been deleted
        self.assertEqual(
            count_perm_base - 5,
            GroupForumPermission.objects.filter(
                forum=forum, group=base_group, has_perm=True
            ).count(),
        )

        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=base_group, has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

    def test_course_student_course_locked_student_connects_before(self):
        """
        We create a student before and then an instructor.
        The instructor locks the course. The students reconnects
        after, the course should be locked.
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

        # course is locked
        url_lock = f"/forum/admin/lock-course/{forum.id}/"
        response = self.client.post(url_lock, follow=True)
        self.assertEqual(200, response.status_code)

        # course is now marked as locked
        context.refresh_from_db()
        self.assertEqual(context.is_marked_locked, True)

        # reconnect the student user
        self._connects("student")
        # no new user has been created
        self.assertEqual(user_count, User.objects.count())

        # info is present in forums view
        response = self.client.get("/forum/")
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        # info is present in the forum view
        url_forum = f"/forum/forum/{forum.slug}-{forum.pk}/"
        response = self.client.get(url_forum)
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        url_topic_create = f"{url_forum}topic/create/"
        # user is a student but he can't create a new topic anymore
        self.assertNotContains(
            response,
            f'<a href="{url_topic_create}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comments fa-lg"></i>&nbsp;New topic</a>',
            html=True,
        )

        # info is present in topic view
        response = self.client.get(
            f"{url_forum}topic/{post.topic.slug}-{post.topic.pk}/"
        )
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )

        # permissions of the base group have been deleted
        self.assertEqual(
            count_perm_base - 5,
            GroupForumPermission.objects.filter(
                forum=forum, group=base_group, has_perm=True
            ).count(),
        )

        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=base_group, has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(403, response.status_code)

        # user can't answer a post anymore
        url_topic = f"{url_forum}topic/{post.topic.slug}-{post.topic.pk}/"
        response = self.client.get(url_topic, follow=True)
        url_topic_reply = f"{url_topic}post/create/"
        self.assertNotContains(
            response,
            f'<a href="{url_topic_reply}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comment fa-lg"></i>&nbsp;Post reply</a>',
            html=True,
        )
        response = self.client.get(url_topic_reply, follow=True)
        self.assertEqual(403, response.status_code)

    def test_course_student_course_locked_admin_connects_before(self):
        """
        Instructor connects and lock the course, then the student connects
        himself. We check that when the user wasn't connected before the
        locking, he can see the course info as locked and he can't create
        new topic or reply to post.
        """
        forum = self._connects("instructor")
        # create a post in the forum
        post = PostFactory(topic=TopicFactory(forum=forum))
        # context object has been created
        context = LTIContext.objects.get(lti_id=self.context_id)
        # course is locked
        url_lock = f"/forum/admin/lock-course/{forum.id}/"
        response = self.client.post(url_lock, follow=True)
        self.assertEqual(200, response.status_code)

        # course is now marked as locked
        context.refresh_from_db()
        self.assertEqual(context.is_marked_locked, True)

        # connects the student
        self._connects("student")

        # info is present in forums view
        response = self.client.get("/forum/")
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        # info is present in the forum view
        url_forum = f"/forum/forum/{forum.slug}-{forum.pk}/"
        response = self.client.get(url_forum)
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        url_topic_create = f"{url_forum}topic/create/"
        # user is student but he can't create a new topic anymore
        self.assertNotContains(
            response,
            f'<a href="{url_topic_create}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comments fa-lg"></i>&nbsp;New topic</a>',
            html=True,
        )

        # info is present in topic view
        response = self.client.get(
            f"{url_forum}topic/{post.topic.slug}-{post.topic.pk}/"
        )
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )

        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(403, response.status_code)

        # user can't answer a post anymore
        url_topic = f"{url_forum}topic/{post.topic.slug}-{post.topic.pk}/"
        response = self.client.get(url_topic, follow=True)
        url_topic_reply = f"{url_topic}post/create/"
        self.assertNotContains(
            response,
            f'<a href="{url_topic_reply}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comment fa-lg"></i>&nbsp;Post reply</a>',
            html=True,
        )
        response = self.client.get(url_topic_reply, follow=True)
        self.assertEqual(403, response.status_code)

    def test_course_create_multiple_forums(self):
        """
        Instructor locks the course that has multiple forums.
        Checks the student can't write in a forum other than
        the one from which it has been locked.
        """
        self._connects("instructor")
        forum2 = ForumFactory()
        forum3 = ForumFactory()
        # connects user and add forums to the lti_context
        forum2 = self._connects("instructor", forum_uuid=forum2.lti_id)
        forum3 = self._connects("instructor", forum_uuid=forum3.lti_id)

        # create a post in forum3
        post = PostFactory(topic=TopicFactory(forum=forum3))
        response = self.client.post(
            f"/forum/admin/lock-course/{forum2.id}/", follow=True
        )
        self.assertEqual(200, response.status_code)

        # course is now marked as locked
        context = LTIContext.objects.get(lti_id=self.context_id)
        self.assertEqual(context.is_marked_locked, True)

        # student connection
        self._connects("student")

        # info is present in forums view
        response = self.client.get("/forum/")
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        # info is present in the forum3 view
        url_forum3 = f"/forum/forum/{forum3.slug}-{forum3.pk}/"
        response = self.client.get(url_forum3)
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        url_topic_create = f"{url_forum3}topic/create/"
        # user is student but he can't create a new topic anymore
        self.assertNotContains(
            response,
            f'<a href="{url_topic_create}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comments fa-lg"></i>&nbsp;New topic</a>',
            html=True,
        )
        # info is present in topic view
        response = self.client.get(
            f"{url_forum3}topic/{post.topic.slug}-{post.topic.pk}/"
        )
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )

        # can't create a topic
        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(403, response.status_code)

        # user can't answer a post anymore
        url_topic = f"{url_forum3}topic/{post.topic.slug}-{post.topic.pk}/"
        response = self.client.get(url_topic, follow=True)
        url_topic_reply = f"{url_topic}post/create/"
        self.assertNotContains(
            response,
            f'<a href="{url_topic_reply}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comment fa-lg"></i>&nbsp;Post reply</a>',
            html=True,
        )
        response = self.client.get(url_topic_reply, follow=True)
        self.assertEqual(403, response.status_code)

    def test_course_create_forum_after_lock(self):
        """
        Instructor locks the course, then a student connects.
        After the course is locked, the instructor reconnects and
        then creates a new forum whereas the course is supposed
        to be locked. We check that the student still can't reply
        or add topic in this new forum created after the locked.
        """
        forum = self._connects("instructor")

        response = self.client.post(
            f"/forum/admin/lock-course/{forum.id}/", follow=True
        )
        self.assertEqual(200, response.status_code)

        # course is now marked as locked
        context = LTIContext.objects.get(lti_id=self.context_id)
        self.assertEqual(context.is_marked_locked, True)

        # student connection
        self._connects("student", uuid="NewOne", lis_person_sourcedid="enzo")

        # a new Forum is created after the locking
        forum2 = ForumFactory()
        forum2 = self._connects("instructor", forum_uuid=forum2.lti_id)
        # create a post in forum3
        post = PostFactory(topic=TopicFactory(forum=forum2))

        # student reconnects
        self._connects("student", uuid="NewOne", lis_person_sourcedid="enzo")
        # user can only read the forum
        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum2, group=context.get_base_group(), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        # info is present in forums view
        response = self.client.get("/forum/")
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        # info is present in the forum4 view
        url_forum2 = f"/forum/forum/{forum2.slug}-{forum2.pk}/"
        response = self.client.get(url_forum2)
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        url_topic_create = f"{url_forum2}topic/create/"
        # user is student but he can't create a new topic anymore
        self.assertNotContains(
            response,
            f'<a href="{url_topic_create}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comments fa-lg"></i>&nbsp;New topic</a>',
            html=True,
        )
        # info is present in topic view
        response = self.client.get(
            f"{url_forum2}topic/{post.topic.slug}-{post.topic.pk}/"
        )
        self.assertContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )

        # still can't create a topic event if the forum was created after
        response = self.client.get(url_topic_create, follow=True)
        self.assertEqual(403, response.status_code)

        # user can't answer a post anymore
        url_topic = f"{url_forum2}topic/{post.topic.slug}-{post.topic.pk}/"
        response = self.client.get(url_topic, follow=True)
        url_topic_reply = f"{url_topic}post/create/"
        self.assertNotContains(
            response,
            f'<a href="{url_topic_reply}" class="btn btn-primary btn-sm">'
            '<i class="fa fa-comment fa-lg"></i>&nbsp;Post reply</a>',
            html=True,
        )
        response = self.client.get(url_topic_reply, follow=True)
        self.assertEqual(403, response.status_code)

    def test_course_admin_cant_lock_forum_in_other_context(self):
        """
        Instructors can't lock course from a forum that isn't
        in the same context.
        """
        forum = self._connects("instructor")
        forum_other_context = ForumFactory()

        # user can't access the view to lock a course
        response = self.client.get(
            f"/forum/admin/lock-course/{forum_other_context.id}/"
        )
        self.assertEqual(403, response.status_code)

        # user can access the view to lock a course
        response = self.client.get(f"/forum/admin/lock-course/{forum.id}/")
        self.assertEqual(200, response.status_code)

    def test_course_connection_no_lti(self):
        """
        LTI session is not set then page can still be viewed, the notice
        about the course being locked won't appear
        """
        forum = self._connects("instructor")
        post = PostFactory(topic=TopicFactory(forum=forum))
        # instructor locks the forum
        response = self.client.get(f"/forum/admin/lock-course/{forum.id}/")
        self.assertEqual(200, response.status_code)

        # user connected without LTI Session
        user = UserFactory()
        assign_perm("can_read_forum", user, forum)
        self.client.force_login(user)

        # info is not present even if the course is locked

        # - in forums view but page is available
        response = self.client.get("/forum/")
        self.assertNotContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )
        # - in the forum view
        response = self.client.get(f"/forum/forum/{forum.slug}-{forum.pk}/")
        self.assertNotContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )

        # - in topic view
        response = self.client.get(
            f"/forum/forum/{forum.slug}-{forum.pk}/topic/{post.topic.slug}-{post.topic.pk}/"
        )
        self.assertNotContains(
            response,
            "This course has locked forums, non admin users can only read the history.",
        )

    def test_command_on_a_lock_forum(self):
        """
        Check if the sync_group_permissions command is used on a locked forum,
        that students don't get back any of the default's writting permission.
        """
        # Create a LTI context and a forum
        forum = self._connects("instructor")
        context = LTIContext.objects.get(lti_id=self.context_id)

        # initialy student and base group have these permissions
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
        self.assertEqual(
            [],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_role_group("student"), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        # Lock the forum
        self.client.post(f"/forum/admin/lock-course/{forum.id}/")

        # then student and base group have lost permissions
        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_base_group(), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        # Run the command with the --apply argument, to execute real database updates
        call_command("sync_group_permissions", "--apply")

        # no new permission have been added for these two groups
        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_base_group(), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

        # student group still contains no permission
        self.assertEqual(
            [],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_role_group("student"), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

    def test_is_marked_locked_set_in_the_back(self):
        """
        Check when the tag is_marked_locked is set to True out of a web navigation
        that the forum gets blocked anyway
        """
        forum = self._connects("instructor")
        context = LTIContext.objects.get(lti_id=self.context_id)
        context.is_marked_locked = True
        context.save()
        self.assertEqual(context.is_marked_locked, True)

        # connects the student
        self._connects("student", uuid="NewOne", lis_person_sourcedid="enzo")

        # standard users can only read the forum
        self.assertEqual(
            ["can_see_forum", "can_read_forum"],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_base_group(), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )
        self.assertEqual(
            [],
            list(
                GroupForumPermission.objects.filter(
                    forum=forum, group=context.get_role_group("student"), has_perm=True
                ).values_list("permission__codename", flat=True)
            ),
        )

    def test_course_create_multiple_forums_listing_on(self):
        """
        Instructor wants to lock the course that has multiple forums.
        The list of forums should be displayed before the confirmation's
        button.
        """
        forum1 = self._connects("instructor")
        forum2 = ForumFactory(name="Forum2")
        forum3 = ForumFactory(name="Forum3")
        # connects user and add forums to the lti_context
        forum2 = self._connects("instructor", forum_uuid=forum2.lti_id)
        forum3 = self._connects("instructor", forum_uuid=forum3.lti_id)

        # go on the page to lock the course from the forum1
        response = self.client.get(f"/forum/admin/lock-course/{forum1.id}/")
        self.assertEqual(200, response.status_code)
        # this listing is common for all the forums of the course
        forums_list = (
            f'<p class="ml-3 mb-0"><strong>{forum1.name}</strong></p>'
            '<p class="ml-3 mb-0"><strong>Forum2</strong></p>'
            '<p class="ml-3 mb-0"><strong>Forum3</strong></p>'
        )
        self.assertContains(response, forums_list)

        # go on the page to lock the course from the forum2
        response = self.client.get(f"/forum/admin/lock-course/{forum2.id}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, forums_list)

        # go on the page to lock the course from the forum3
        response = self.client.get(f"/forum/admin/lock-course/{forum3.id}/")
        self.assertEqual(200, response.status_code)
        self.assertContains(response, forums_list)
