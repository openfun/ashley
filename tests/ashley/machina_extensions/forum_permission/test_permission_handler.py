from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model
from machina.core.loading import get_class

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

PermissionHandler = get_class("forum_permission.handler", "PermissionHandler")
Forum = get_model("forum", "Forum")


class PermissionHandlerTestCase(TestCase):
    """Test the ForumPermission middleware"""

    def test_forum_list(self):
        user = UserFactory()
        lti_context_a = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context_b = LTIContextFactory(lti_consumer=user.lti_consumer)

        # Create 2 forums for context A
        forum_a1 = ForumFactory(name="Forum A1")
        forum_a1.lti_contexts.add(lti_context_a)
        forum_a2 = ForumFactory(name="Forum A2")
        forum_a2.lti_contexts.add(lti_context_a)
        # Create 2 forums for context B
        forum_b1 = ForumFactory(name="Forum B1")
        forum_b1.lti_contexts.add(lti_context_b)
        forum_b2 = ForumFactory(name="Forum B2")
        forum_b2.lti_contexts.add(lti_context_b)

        # Grant read-only access for forums A1, A2 and B1 to our user
        assign_perm("can_see_forum", user, forum_a1, True)
        assign_perm("can_read_forum", user, forum_a1, True)
        assign_perm("can_see_forum", user, forum_a2, True)
        assign_perm("can_read_forum", user, forum_a2, True)
        assign_perm("can_see_forum", user, forum_b1, True)
        assign_perm("can_read_forum", user, forum_b1, True)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session

        # Make a request to get the forum list, with an empty session
        response = self.client.get("/forum/")
        # We should see all forums we have access to
        self.assertContains(response, "Forum A1")
        self.assertContains(response, "Forum A2")
        self.assertContains(response, "Forum B1")
        self.assertNotContains(response, "Forum B2")

        # Update the client session to limit the user to the LTIContext A
        # Make a request to get he forum list again
        session[SESSION_LTI_CONTEXT_ID] = lti_context_a.id
        session.save()
        response = self.client.get("/forum/")

        # We should see only forums related to LTIContext A
        self.assertContains(response, "Forum A1")
        self.assertContains(response, "Forum A2")
        self.assertNotContains(response, "Forum B1")
        self.assertNotContains(response, "Forum B2")

        # Update the client session to limit the user to the LTIContext B
        # Make a request to get he forum list again
        session[SESSION_LTI_CONTEXT_ID] = lti_context_b.id
        session.save()
        response = self.client.get("/forum/")

        # We should see only forum B1
        self.assertNotContains(response, "Forum A1")
        self.assertNotContains(response, "Forum A2")
        self.assertContains(response, "Forum B1")
        self.assertNotContains(response, "Forum B2")

    def test_get_readable_forums(self):
        """
        The get_readable_forums() function should filter the results according
        to the LTIContext of the user, if available.
        """
        user = UserFactory()
        lti_context_a = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context_b = LTIContextFactory(lti_consumer=user.lti_consumer)

        # Create 2 forums for context A
        forum_a1 = ForumFactory(name="Forum A1")
        forum_a1.lti_contexts.add(lti_context_a)
        forum_a2 = ForumFactory(name="Forum A2")
        forum_a2.lti_contexts.add(lti_context_a)
        # Create 2 forums for context B
        forum_b1 = ForumFactory(name="Forum B1")
        forum_b1.lti_contexts.add(lti_context_b)
        forum_b2 = ForumFactory(name="Forum B2")
        forum_b2.lti_contexts.add(lti_context_b)

        # Grant read-only access for forums A1, A2 and B1 to our user
        assign_perm("can_see_forum", user, forum_a1, True)
        assign_perm("can_read_forum", user, forum_a1, True)
        assign_perm("can_see_forum", user, forum_a2, True)
        assign_perm("can_read_forum", user, forum_a2, True)
        assign_perm("can_see_forum", user, forum_b1, True)
        assign_perm("can_read_forum", user, forum_b1, True)

        # Instantiate the permission Handler
        permission_handler = PermissionHandler()

        # When the permission handler has no lti context specified,
        # the get_readable_forums should return all forums the user
        # has access to
        forums_qs = Forum.objects.all()
        forums_list = list(Forum.objects.all())
        readable_forums = permission_handler.get_readable_forums(forums_qs, user)
        self.assertCountEqual(readable_forums, [forum_a1, forum_a2, forum_b1])

        # Inject a LTI context into the permission handler and ensure that
        # the results are filtered according to it
        permission_handler.current_lti_context_id = lti_context_a.id
        readable_forums = permission_handler.get_readable_forums(forums_qs, user)
        self.assertCountEqual(readable_forums, [forum_a1, forum_a2])

        # Check the same with a list of forums instead of a QuerySet
        readable_forums = permission_handler.get_readable_forums(forums_list, user)
        self.assertCountEqual(readable_forums, [forum_a1, forum_a2])

        # Inject another LTIContext into the permission handler
        permission_handler.current_lti_context_id = lti_context_b.id
        readable_forums = permission_handler.get_readable_forums(forums_qs, user)
        self.assertCountEqual(readable_forums, [forum_b1])
        readable_forums = permission_handler.get_readable_forums(forums_list, user)
        self.assertCountEqual(readable_forums, [forum_b1])

    def test_get_readable_forums_no_archives(self):
        """
        The get_readable_forums() function should filter the results and not return
        archived forums with or without LTIContext
        """
        user = UserFactory()
        lti_context_a = LTIContextFactory(lti_consumer=user.lti_consumer)
        lti_context_b = LTIContextFactory(lti_consumer=user.lti_consumer)

        # Create 2 forums for context A, with forum_a1 as an archived one
        forum_a1 = ForumFactory(name="Forum A1", archived=True)
        forum_a1.lti_contexts.add(lti_context_a)
        forum_a2 = ForumFactory(name="Forum A2")
        forum_a2.lti_contexts.add(lti_context_a)
        # Create 1 forum for context B
        forum_b1 = ForumFactory(name="Forum B1")
        forum_b1.lti_contexts.add(lti_context_b)

        # Grant read-only access for forums A1, A2 and B1 to our user
        assign_perm("can_see_forum", user, forum_a1, True)
        assign_perm("can_read_forum", user, forum_a1, True)
        assign_perm("can_see_forum", user, forum_a2, True)
        assign_perm("can_read_forum", user, forum_a2, True)
        assign_perm("can_see_forum", user, forum_b1, True)
        assign_perm("can_read_forum", user, forum_b1, True)

        # Instantiate the permission Handler
        permission_handler = PermissionHandler()

        # When the permission handler has no lti context specified,
        # the get_readable_forums should return all forums the user
        # has access to
        forums_qs = Forum.objects.all()
        forums_list = list(Forum.objects.all())
        readable_forums = permission_handler.get_readable_forums(forums_qs, user)
        self.assertCountEqual(readable_forums, [forum_a2, forum_b1])

        # Check the same with a list of forums instead of a QuerySet
        readable_forums = permission_handler.get_readable_forums(forums_list, user)
        self.assertCountEqual(readable_forums, [forum_a2, forum_b1])

        # Inject a LTI context into the permission handler and ensure that
        # the results are filtered according to it
        permission_handler.current_lti_context_id = lti_context_a.id
        readable_forums = permission_handler.get_readable_forums(forums_qs, user)
        self.assertCountEqual(readable_forums, [forum_a2])

        # Check the same with a list of forums instead of a QuerySet
        readable_forums = permission_handler.get_readable_forums(forums_list, user)
        self.assertCountEqual(readable_forums, [forum_a2])

    def test_get_readable_forums_super_user(self):
        """
        Super user has access to all the forum filtered on LTIContext and
        archived ones but don't need to have access in reading.
        """
        super_user = UserFactory(is_superuser=True)
        basic_user = UserFactory()
        lti_context_a = LTIContextFactory(lti_consumer=super_user.lti_consumer)
        lti_context_b = LTIContextFactory(lti_consumer=super_user.lti_consumer)

        # Create 2 forums for context A
        forum_a1 = ForumFactory(name="Forum A1")
        forum_a1.lti_contexts.add(lti_context_a)
        forum_a2_archived = ForumFactory(name="Forum A2")
        forum_a2_archived.lti_contexts.add(lti_context_a)
        forum_a2_archived.archived = True
        forum_a2_archived.save()
        # Create 1 forum for context B
        forum_b1 = ForumFactory(name="Forum B1")
        forum_b1.lti_contexts.add(lti_context_b)

        # Instantiate the permission Handler
        permission_handler = PermissionHandler()

        forums_qs = Forum.objects.all()
        # With no lti_context super_user can see all forums
        readable_forums = permission_handler.get_readable_forums(forums_qs, super_user)
        self.assertCountEqual(readable_forums, [forum_a1, forum_b1])
        # standard user can't see any
        readable_forums = permission_handler.get_readable_forums(forums_qs, basic_user)
        self.assertCountEqual(readable_forums, [])

        # Inject a LTI context into the permission handler and ensure that
        # the results are filtered according to it
        permission_handler.current_lti_context_id = lti_context_a.id
        readable_forums = permission_handler.get_readable_forums(forums_qs, super_user)
        # even if super user has no can_read_forum permission is still can see all
        # unarchived forums of his lti_context
        self.assertCountEqual(readable_forums, [forum_a1])

        # standard user can't see any
        readable_forums = permission_handler.get_readable_forums(forums_qs, basic_user)
        self.assertCountEqual(readable_forums, [])
