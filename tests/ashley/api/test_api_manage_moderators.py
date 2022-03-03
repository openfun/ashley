"""Tests API to manage moderators."""
import json
import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.defaults import _FORUM_ROLE_MODERATOR
from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

User = get_user_model()


class ManageModeratorApiTest(TestCase):
    """Test the API to manage moderators."""

    def test_access_basic_api_manage_moderator_list_users(self):
        """Anonymous users should not be allowed to retrieve list of users."""
        response = self.client.get("/api/v1.0/users/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_can_manage_moderators_moderator_list_users(self):
        """Users that can manage moderators should be able to use the API to request
        list of users"""
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/api/v1.0/users/")
        # First it's forbidden
        self.assertEqual(403, response.status_code)
        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1.0/users/")
        # Still forbidden session ok but missing permission
        self.assertEqual(response.status_code, 403)

        assign_perm("can_manage_moderator", user, forum, True)
        # Should now be authorized
        response = self.client.get("/api/v1.0/users/")
        self.assertEqual(response.status_code, 200)

    def test_access_basic_api_manage_moderator_list_students(self):
        """Anonymous users should not be allowed to retrieve list of students."""
        response = self.client.get("/api/v1.0/users/?role=student")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_can_manage_moderators_moderator_list_students(self):
        """Users that can manage moderators should be able to use the API to request
        list of students"""
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/api/v1.0/users/?role=student")
        # First it's forbidden
        self.assertEqual(403, response.status_code)
        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1.0/users/?role=student")
        # Still forbidden session ok but missing permission
        self.assertEqual(response.status_code, 403)

        assign_perm("can_manage_moderator", user, forum, True)
        # Should now be authorized
        response = self.client.get("/api/v1.0/users/?role=student")
        self.assertEqual(response.status_code, 200)

    def test_access_basic_api_manage_moderator_list_moderators(self):
        """Anonymous users should not be allowed to retrieve list of moderators."""
        response = self.client.get("/api/v1.0/users/?role=moderator")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_can_manage_moderators_list_moderators(self):
        """Users that can manage moderators should be able to use the API to request
        list of moderators"""
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/api/v1.0/users/?role=moderator")

        # First it's forbidden
        self.assertEqual(403, response.status_code)

        # Add permission
        assign_perm("can_manage_moderator", user, forum, True)

        # Still forbidden, missing the session
        response = self.client.get("/api/v1.0/users/?role=moderator")
        self.assertEqual(403, response.status_code)

        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1.0/users/?role=moderator")
        # Permission + session added, it should be allowed
        self.assertEqual(response.status_code, 200)

    def test_access_basic_api_manage_moderator_list_instructors(self):
        """Anonymous users should not be allowed to retrieve list of instructors."""
        response = self.client.get("/api/v1.0/users/?role=instructor")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_can_manage_moderators_moderator_list_instructors(self):
        """Users that can manage moderators should be able to use the API to request
        list of instructors"""
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/api/v1.0/users/?role=instructor")
        # First it's forbidden
        self.assertEqual(403, response.status_code)
        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1.0/users/?role=instructor")
        # Still forbidden session ok but missing permission
        self.assertEqual(response.status_code, 403)

        assign_perm("can_manage_moderator", user, forum, True)
        # Should now be authorized
        response = self.client.get("/api/v1.0/users/?role=instructor")
        self.assertEqual(response.status_code, 200)

    def test_access_basic_api_manage_moderator_list_not_moderators(self):
        """Anonymous users should not be allowed to retrieve list of non moderators."""
        response = self.client.get("/api/v1.0/users/?role=!moderator")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_can_manage_moderators_list_non_moderators(self):
        """Users that can manage moderators should be able to use the API to request
        list of users that are not moderators"""
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        response = self.client.get("/api/v1.0/users/?role=!moderator")

        # First it's forbidden
        self.assertEqual(403, response.status_code)

        # Add permission
        assign_perm("can_manage_moderator", user, forum, True)

        # Still forbidden, missing the session
        response = self.client.get("/api/v1.0/users/?!role=moderator")
        self.assertEqual(403, response.status_code)

        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1.0/users/?role=!moderator")
        # Permission + session added, it should be allowed
        self.assertEqual(response.status_code, 200)

    def test_access_api_update_student_post(self):
        """Standard call should not be allowed to update a student."""
        # Creates a forum
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        data = {
            "public_username": "toto",
        }
        response = self.client.patch(
            f"/api/v1.0/users/{user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

    def test_access_api_update_student_patch(self):
        """Standard call should not be allowed to update a student by patch."""
        # Creates a forum
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        data = {
            "public_username": "toto",
        }
        response = self.client.patch(
            f"/api/v1.0/users/{user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

    def test_access_api_update_student_put(self):
        """Standard call should not be allowed to update a student by put."""
        # Creates a forum
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        data = {
            "public_username": "toto",
        }
        response = self.client.put(
            f"/api/v1.0/users/{user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

    def test_access_api_update_instructor_post(self):
        """Post to update user is not allowed."""
        # Creates a forum
        user = UserFactory()
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        lti_context.sync_user_groups(user, ["instructor"])
        assign_perm("can_manage_moderator", user, forum, True)
        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        response = self.client.post(
            f"/api/v1.0/users/{user.id}/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 405)
        content = json.loads(response.content)
        self.assertEqual(content, {"detail": 'Method "POST" not allowed.'})

    def test_access_api_update_instructor_patch(self):
        """Standard instructor call to patch user is allowed but doesn't change anything."""
        # Creates a forum
        user = UserFactory(id=1, public_username="user")
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        lti_context.sync_user_groups(user, ["instructor"])
        assign_perm("can_manage_moderator", user, forum, True)
        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        response = self.client.patch(
            f"/api/v1.0/users/{user.id}/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {"id": 1, "public_username": "user"})

    def test_access_api_update_instructor_put(self):
        """Standard instructor call to put user is allowed but doesn't change anything."""
        # Creates a forum
        user = UserFactory(id=1, public_username="user")
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        lti_context.sync_user_groups(user, ["instructor"])
        assign_perm("can_manage_moderator", user, forum, True)
        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        response = self.client.put(
            f"/api/v1.0/users/{user.id}/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {"id": 1, "public_username": "user"})

    def test_access_api_moderator_group_anonymous_patch(self):
        """anonymous can't patch user to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.patch(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_api_moderator_group_anonymous_post(self):
        """anonymous can't update user to add or remove  the group moderator."""
        user = UserFactory(public_username="user")
        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.post(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_api_moderator_group_anonymous_put(self):
        """anonymous can't update user with a put to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.put(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_api_moderator_group_student_patch(self):
        """Student can't patch user to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        # Creates a forum
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.patch(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

    def test_access_api_moderator_group_student_post(self):
        """student can't update user to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        # Creates a forum
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.post(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

    def test_access_api_moderator_group_student_put(self):
        """Student can't update user with a put to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        # Creates a forum
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.put(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

    def test_access_api_moderator_group_student_patch(self):
        """Student can't patch user to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        # Creates a forum
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_read_forum", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.patch(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

    def test_access_api_moderator_group_instructor_post(self):
        """Instructor can't update user with a POST to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        # Creates a forum
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_manage_moderator", user, forum, True)

        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.post(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 405)
        content = json.loads(response.content)
        self.assertEqual(content, {"detail": 'Method "POST" not allowed.'})

    def test_access_api_moderator_group_instructor_put(self):
        """Instructor can't update user with a put to add or remove the group moderator."""
        user = UserFactory(public_username="user")
        # Creates a forum
        lti_context = LTIContextFactory(lti_consumer=user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        assign_perm("can_manage_moderator", user, forum, True)
        # Creates the session
        self.client.force_login(user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        action = random.choice(["add_group_moderator", "remove_group_moderator"])
        response = self.client.put(f"/api/v1.0/users/{user.id}/{action}/")
        self.assertEqual(response.status_code, 405)
        content = json.loads(response.content)
        self.assertEqual(content, {"detail": 'Method "PUT" not allowed.'})

    def test_access_api_can_manage_moderators_update_student_promote_revoke(self):
        """
        Promote and revoke a user with right context, permission, group
        Test to validate that update request API is working when everything
        is set properly.
        """
        update_user = UserFactory(public_username="Thérèse")
        api_user = UserFactory(lti_consumer=update_user.lti_consumer)

        lti_context = LTIContextFactory(lti_consumer=update_user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        # Assign student group to user
        lti_context.sync_user_groups(update_user, ["student"])
        # Check list group of the user
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

        # Assign the permission
        assign_perm("can_manage_moderator", api_user, forum, True)
        # Creates the session
        self.client.force_login(api_user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        # Promote user to moderator
        response = self.client.patch(
            f"/api/v1.0/users/{update_user.id}/add_group_moderator/",
            content_type="application/json",
        )
        print("Response, ", response.content)
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {"id": 1, "public_username": "Thérèse"})

        # Check group moderator is part of group of the user
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
                f"{lti_context.base_group_name}:role:moderator",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

        # Then Revoke user to moderator
        response = self.client.patch(
            f"/api/v1.0/users/{update_user.id}/remove_group_moderator/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {"id": 1, "public_username": "Thérèse"})

        # Check group moderator is not part of users's group
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

    def test_access_api_can_manage_moderators_update_student_no_group_context(self):
        """Users that don't have a group from this context can't be promoted moderator"""
        update_user = UserFactory()
        api_user = UserFactory(lti_consumer=update_user.lti_consumer)

        lti_context = LTIContextFactory(lti_consumer=update_user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        update_user.refresh_from_db()
        # Assign the permission
        assign_perm("can_manage_moderator", api_user, forum, True)
        # Creates the session
        self.client.force_login(api_user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        # Data to promote user to moderator
        response = self.client.patch(
            f"/api/v1.0/users/{update_user.id}/add_group_moderator/",
            content_type="application/json",
        )
        
        self.assertEqual(response.status_code, 404)#why 404 consider user doesn't exist...because of db relationnal ?
        
        # Add group student and it should work
        lti_context.sync_user_groups(update_user, ["student"])
        response = self.client.patch(
            f"/api/v1.0/users/{update_user.id}/add_group_moderator/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_access_api_can_manage_moderators_update_student_no_group_moderator(self):
        """If moderator group doesn't exist user can be updated and group created
        Case for forum created before this feature"""
        update_user = UserFactory()
        api_user = UserFactory(lti_consumer=update_user.lti_consumer)

        lti_context = LTIContextFactory(lti_consumer=update_user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        # Add group student
        lti_context.sync_user_groups(update_user, ["student"])
        # Assign the permission
        assign_perm("can_manage_moderator", api_user, forum, True)
        # Creates the session
        self.client.force_login(api_user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        # Data to promote user to moderator
        response = self.client.patch(
            f"/api/v1.0/users/{update_user.id}/add_group_moderator/",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_access_api_can_manage_moderators_update_student_no_session(self):
        """Users with no session can't update user"""
        update_user = UserFactory()
        api_user = UserFactory(lti_consumer=update_user.lti_consumer)

        lti_context = LTIContextFactory(lti_consumer=update_user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        # Assign student group to user
        lti_context.sync_user_groups(update_user, ["student"])
        # Assign the permission
        assign_perm("can_manage_moderator", api_user, forum, True)
        #
        data = {
            "roles": ["moderator"],
        }
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )
        # Create the session and it should work
        self.client.force_login(api_user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def _login_authorized_user_to_manage_moderators(self):
        """
        Access to API has been tested in previous tests. This method is a shortcut for tests
        below to retrieve a granted user for the API and the current lti_context.
        """
        api_user = UserFactory()

        lti_context = LTIContextFactory(lti_consumer=api_user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)
        # Assign the permission for API user
        assign_perm("can_manage_moderator", api_user, forum, True)

        # Create the session and it should work
        self.client.force_login(api_user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        return api_user, lti_context

    def test_access_api_can_manage_moderators_update_student_no_role(self):
        """If roles is not present or is defined to unexpected value, promote moderator is
        not allowed"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()
        # Creates user to update
        update_user = UserFactory(lti_consumer=api_user.lti_consumer)
        lti_context.sync_user_groups(update_user, ["student"])

        data = {
            "id": update_user.id,
        }
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )
        # Change data, add role parameter to ’whatever’
        data = {"roles": ["whatever"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        # Change data, add roles parameter to ’instructor’, it's not allowed
        data = {"roles": ["instructor"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        # Change data, add roles parameter to ’moderator’ and it should work
        data = {"roles": ["moderator"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_revoke_moderator_on_student(self):
        """A user that is not moderator can't be revoked"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        # Creates user to update
        update_user = UserFactory(lti_consumer=api_user.lti_consumer)
        lti_context.sync_user_groups(update_user, ["student"])

        data = {"roles": ["student"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )

        # Assign moderator group to user
        lti_context.sync_user_groups(update_user, ["student", "moderator"])
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
                f"{lti_context.base_group_name}:role:moderator",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

        # Revoke should now be ok
        data = {"id": update_user.id, "roles": ["student"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # Check group moderator is not part of users's group
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

    def test_promote_on_moderator_student(self):
        """A user that is a moderator can't be promoted"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        # Assign moderator group to user
        update_user = UserFactory(lti_consumer=api_user.lti_consumer)
        lti_context.sync_user_groups(update_user, ["student", "moderator"])
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
                f"{lti_context.base_group_name}:role:moderator",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )
        # Promote shouldn't work
        data = {"roles": ["moderator"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )
        # Revoke should work
        data = {"id": update_user.id, "roles": ["student"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )
        # Now promote should work
        data = {"id": update_user.id, "roles": ["moderator"]}
        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
                f"{lti_context.base_group_name}:role:moderator",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

    def test_list_users(self):
        """Controls that the list returned by the API contains expected users"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        user2 = UserFactory(
            public_username="Aurélie", lti_consumer=api_user.lti_consumer
        )
        user3 = UserFactory(public_username="Abba", lti_consumer=api_user.lti_consumer)
        user4 = UserFactory(
            public_username="Silvio", lti_consumer=api_user.lti_consumer
        )
        UserFactory(public_username="Abdel", lti_consumer=api_user.lti_consumer)
        lti_context.sync_user_groups(user1, ["student"])
        lti_context.sync_user_groups(user2, ["student"])
        lti_context.sync_user_groups(user3, ["student", "moderator"]),
        lti_context.sync_user_groups(user4, ["instructor"])

        with self.assertNumQueries(9):
            # Request with no filter returns the list of users but user5 that has no roles
            # list ordered by public_username
            response = self.client.get(
                "/api/v1.0/users/", content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(
                content,
                [
                    {
                        "id": user3.id,
                        "public_username": "Abba",
                    },
                    {"id": user2.id, "public_username": "Aurélie"},
                    {"id": user4.id, "public_username": "Silvio"},
                    {"id": user1.id, "public_username": "Thomas"},
                ],
            )

        with self.assertNumQueries(9):
            response = self.client.get(
                "/api/v1.0/users/?role=student", content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(
                content,
                [
                    {
                        "id": user3.id,
                        "public_username": "Abba",
                    },
                    {"id": user2.id, "public_username": "Aurélie"},
                    {"id": user1.id, "public_username": "Thomas"},
                ],
            )

        with self.assertNumQueries(9):
            response = self.client.get(
                "/api/v1.0/users/?role=moderator", content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(
                content,
                [
                    {
                        "id": user3.id,
                        "public_username": "Abba",
                    },
                ],
            )

        with self.assertNumQueries(9):
            response = self.client.get(
                "/api/v1.0/users/?role=!moderator", content_type="application/json"
            )
            self.assertEqual(response.status_code, 200)
            content = json.loads(response.content)
            self.assertEqual(
                content,
                [
                    {"id": user2.id, "public_username": "Aurélie"},
                    {"id": user1.id, "public_username": "Thomas"},
                ],
            )

        response = self.client.get(
            "/api/v1.0/users/?role=instructor", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {"id": user4.id, "public_username": "Silvio"},
            ],
        )

    def test_list_moderators_with_student_groups(self):
        """Creates users with roles student and moderator, this user should be part of the
        list of moderators and be part as well of the list of student group."""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        lti_context.sync_user_groups(user1, ["student", "moderator"])

        # should be part of list student
        response = self.client.get(
            "/api/v1.0/users/?role=student", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user1.id,
                    "public_username": "Thomas",
                },
            ],
        )
        # should be part of list moderator
        response = self.client.get(
            "/api/v1.0/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user1.id,
                    "public_username": "Thomas",
                },
            ],
        )

        # should not be part of list !moderator
        response = self.client.get(
            "/api/v1.0/users/?role=!moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [],
        )

        # should be part of list of users
        response = self.client.get("/api/v1.0/users/", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user1.id,
                    "public_username": "Thomas",
                },
            ],
        )

        # should not be part of list of not moderators
        response = self.client.get(
            "/api/v1.0/users/?role=!moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [],
        )

    def test_list_moderators_with_instructor_groups(self):
        """Creates users with roles instructor and moderator, this user should be part
        of the list of instructor only. Instructors are excluded from moderator list."""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        lti_context.sync_user_groups(user1, ["instructor", "moderator"])

        # student list should be empty
        response = self.client.get(
            "/api/v1.0/users/?role=student", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [],
        )
        # moderator list should be empty because user1 is instructor
        response = self.client.get(
            "/api/v1.0/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [],
        )
        # instructor list should contain user1
        response = self.client.get(
            "/api/v1.0/users/?role=instructor", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user1.id,
                    "public_username": "Thomas",
                },
            ],
        )
        # !moderator list should not contain user1 because user1 is instructor and excluded
        # from not moderators
        response = self.client.get(
            "/api/v1.0/users/?role=!moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [],
        )

        response = self.client.get("/api/v1.0/users/", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user1.id,
                    "public_username": "Thomas",
                },
            ],
        )

    def test_list_users_no_moderator_if_no_group_in_context(self):
        """Controls that list of moderators only concerns users that are part of
        users that have group in this context
        """
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        # add group moderator
        group_moderator = lti_context.get_role_group(_FORUM_ROLE_MODERATOR)
        user1.groups.add(group_moderator)
        user1.save()
        # check user has group moderator
        self.assertCountEqual(
            [f"{lti_context.base_group_name}:role:moderator"],
            list(user1.groups.values_list("name", flat=True)),
        )
        # request users that are moderator
        response = self.client.get(
            "/api/v1.0/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        # should be empty because user has no other groups from this context
        self.assertEqual(content, [])

        # request all users
        response = self.client.get("/api/v1.0/users/", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        # should be empty because user has no other groups from this context
        self.assertEqual(
            content,
            [],
        )

        # request all users that are not moderators
        response = self.client.get(
            "/api/v1.0/users/?role=!moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        # should be empty because user has no other groups from this context
        self.assertEqual(
            content,
            [],
        )

    def test_list_users_moderator_if_group_in_context(self):
        """Controls moderator list"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        # add group moderator and base group of this context
        lti_context.sync_user_groups(user1, ["moderator"])
        # check user has group moderator
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:moderator",
            ],
            list(user1.groups.values_list("name", flat=True)),
        )
        # request users that are moderator
        response = self.client.get(
            "/api/v1.0/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        # user should be in the list because user is moderator and has the base group
        # from this context
        self.assertEqual(
            content,
            [{"id": user1.id, "public_username": "Thomas"}],
        )

        # request all users
        response = self.client.get("/api/v1.0/users/", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        # user should be in the list because user is moderator and has the base group
        # from this context
        self.assertEqual(
            content,
            [{"id": user1.id, "public_username": "Thomas"}],
        )

        # request all users that are not moderators
        response = self.client.get(
            "/api/v1.0/users/?role=!moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        # should be empty because user is moderator
        self.assertEqual(
            content,
            [],
        )

    def test_list_users_are_active_users(self):
        """Controls that list of users and moderators only contains active
        users."""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        user2 = UserFactory(
            public_username="Aurélie", lti_consumer=api_user.lti_consumer
        )
        user4 = UserFactory(is_active=False, lti_consumer=api_user.lti_consumer)
        user3 = UserFactory(is_active=False, lti_consumer=api_user.lti_consumer)
        user5 = UserFactory(public_username="Théo", lti_consumer=api_user.lti_consumer)
        user6 = UserFactory(is_active=False, lti_consumer=api_user.lti_consumer)
        lti_context.sync_user_groups(user1, ["student"])
        lti_context.sync_user_groups(user2, ["student", "moderator"])
        lti_context.sync_user_groups(user3, ["student"])
        lti_context.sync_user_groups(user4, ["student", "moderator"])
        lti_context.sync_user_groups(user5, ["instructor", "moderator"])
        lti_context.sync_user_groups(user6, ["instructor", "moderator"])
        # only active student is listed
        response = self.client.get(
            "/api/v1.0/users/?role=student", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user2.id,
                    "public_username": "Aurélie",
                },
                {"id": user1.id, "public_username": "Thomas"},
            ],
        )
        # only active moderator is listed
        response = self.client.get(
            "/api/v1.0/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user2.id,
                    "public_username": "Aurélie",
                }
            ],
        )
        # only active instructor is listed
        response = self.client.get(
            "/api/v1.0/users/?role=instructor", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {
                    "id": user5.id,
                    "public_username": "Théo",
                }
            ],
        )

        # only active user not moderator is listed
        response = self.client.get(
            "/api/v1.0/users/?role=!moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [{"id": user1.id, "public_username": "Thomas"}],
        )

    def test_api_can_manage_moderators_update_student_public_username_readonly(
        self,
    ):
        """If public_username is present and changed it's not updating the user as its a
        read only data"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()
        # Creates user to update
        update_user = UserFactory(
            public_username="Théo", lti_consumer=api_user.lti_consumer
        )
        lti_context.sync_user_groups(update_user, ["student"])
        # Check group moderator is not part of group list of the user
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

        data = {"roles": ["moderator"], "public_username": "Salomé"}

        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        # Check public_username has been ignored
        self.assertEqual(update_user.public_username, "Théo")
        # Check group moderator is now part of user's groups
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
                f"{lti_context.base_group_name}:role:moderator",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

    def test_api_can_manage_moderators_update_student_id_param_ignored(
        self,
    ):
        """If id in the body of the request is different from the id in the url,
        id is ignored. Only the user targeted in the url is updated."""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()
        # Creates user to update
        update_user = UserFactory(
            public_username="Théo", lti_consumer=api_user.lti_consumer
        )
        useless_user = UserFactory(lti_consumer=api_user.lti_consumer)
        lti_context.sync_user_groups(update_user, ["student"])
        lti_context.sync_user_groups(useless_user, ["student"])

        # Check group moderator is now part of user's groups
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(useless_user.groups.values_list("name", flat=True)),
        )

        # in the body we target the other user
        data = {"id": useless_user.id, "roles": "moderator"}

        response = self.client.put(
            f"/api/v1.0/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        # Check group moderator is now part of user's groups
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
                f"{lti_context.base_group_name}:role:moderator",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )
        # useless_user didn't get updated and still has no moderator group
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(useless_user.groups.values_list("name", flat=True)),
        )
