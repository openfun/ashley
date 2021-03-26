"""Tests for the Thumbnail API."""
import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley import SESSION_LTI_CONTEXT_ID
from ashley.factories import ForumFactory, LTIContextFactory, UserFactory

User = get_user_model()


class ManageModeratorApiTest(TestCase):
    """Test the API to manage moderators."""

    def test_access_basic_api_manage_moderator_list_users(self):
        """Anonymous users should not be allowed to retrieve list of users."""
        response = self.client.get("/api/v1/users/")
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
        response = self.client.get("/api/v1/users/")
        # First it's forbidden
        self.assertEqual(403, response.status_code)
        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1/users/")
        # Still forbidden session ok but missing permission
        self.assertEqual(response.status_code, 403)

        assign_perm("can_manage_moderator", user, forum, True)
        # Should now be authorized
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)

    def test_access_basic_api_manage_moderator_list_students(self):
        """Anonymous users should not be allowed to retrieve list of students."""
        response = self.client.get("/api/v1/users/?role=student")
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
        response = self.client.get("/api/v1/users/?role=student")
        # First it's forbidden
        self.assertEqual(403, response.status_code)
        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1/users/?role=student")
        # Still forbidden session ok but missing permission
        self.assertEqual(response.status_code, 403)

        assign_perm("can_manage_moderator", user, forum, True)
        # Should now be authorized
        response = self.client.get("/api/v1/users/?role=student")
        self.assertEqual(response.status_code, 200)

    def test_access_basic_api_manage_moderator_list_moderators(self):
        """Anonymous users should not be allowed to retrieve list of moderators."""
        response = self.client.get("/api/v1/users/?role=moderator")
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
        response = self.client.get("/api/v1/users/?role=moderator")

        # First it's forbidden
        self.assertEqual(403, response.status_code)

        # Add permission
        assign_perm("can_manage_moderator", user, forum, True)

        # Still forbidden, missing the session
        response = self.client.get("/api/v1/users/?role=moderator")
        self.assertEqual(403, response.status_code)

        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1/users/?role=moderator")
        # Permission + session added, it should be allowed
        self.assertEqual(response.status_code, 200)

    def test_access_basic_api_manage_moderator_list_instructors(self):
        """Anonymous users should not be allowed to retrieve list of instructors."""
        response = self.client.get("/api/v1/users/?role=instructor")
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
        response = self.client.get("/api/v1/users/?role=instructor")
        # First it's forbidden
        self.assertEqual(403, response.status_code)
        # Add session
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()
        self.assertEqual(
            self.client.session.get(SESSION_LTI_CONTEXT_ID), lti_context.id
        )

        response = self.client.get("/api/v1/users/?role=instructor")
        # Still forbidden session ok but missing permission
        self.assertEqual(response.status_code, 403)

        assign_perm("can_manage_moderator", user, forum, True)
        # Should now be authorized
        response = self.client.get("/api/v1/users/?role=instructor")
        self.assertEqual(response.status_code, 200)

    def test_access_api_can_manage_moderators_update_student_promote(self):
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
        data = {
            "role": "moderator",
        }
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {"success": True})

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
        data = {
            "role": "student",
        }
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, {"success": True})

        # Check group moderator is not part of users's group
        self.assertCountEqual(
            [
                lti_context.base_group_name,
                f"{lti_context.base_group_name}:role:student",
            ],
            list(update_user.groups.values_list("name", flat=True)),
        )

    def test_access_api_basic_manage_moderator_update_student(self):
        """Standard call should not be allowed to update a student."""
        user = UserFactory()
        data = {
            "role": "moderator",
        }
        response = self.client.post(
            f"/api/v1/users/{user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "Authentication credentials were not provided."}
        )

    def test_access_api_can_manage_moderators_update_student_no_group_student(self):
        """Users that don't have the group student can't be promoted moderator"""
        update_user = UserFactory()
        api_user = UserFactory(lti_consumer=update_user.lti_consumer)

        lti_context = LTIContextFactory(lti_consumer=update_user.lti_consumer)
        forum = ForumFactory()
        forum.lti_contexts.add(lti_context)

        # Assign the permission
        assign_perm("can_manage_moderator", api_user, forum, True)
        # Creates the session
        self.client.force_login(api_user, "ashley.auth.backend.LTIBackend")
        session = self.client.session
        session[SESSION_LTI_CONTEXT_ID] = lti_context.id
        session.save()

        # Data to promote user to moderator
        data = {
            "role": "moderator",
        }
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )
        # Add group student and it should work
        lti_context.sync_user_groups(update_user, ["student"])
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
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
        data = {
            "role": "moderator",
        }
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
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
            "role": "moderator",
        }
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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
            f"/api/v1/users/{update_user.id}/",
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
        """If role is not present or is defined to unexpected value, promote moderator is
        not allowed"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()
        # Creates user to update
        update_user = UserFactory(lti_consumer=api_user.lti_consumer)
        lti_context.sync_user_groups(update_user, ["student"])

        data = {
            "id": update_user.id,
        }
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )
        # Change data, add role parameter to ’whatever’
        data = {"role": "whatever"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        # Change data, add role parameter to ’instructor’, it's not allowed
        data = {"role": "instructor"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)

        # Change data, add role parameter to ’moderator’ and it should work
        data = {"role": "moderator"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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

        data = {"role": "student"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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
        data = {"id": update_user.id, "role": "student"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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
        """A user that is moderator can't be promoted"""
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
        data = {"role": "moderator"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
            json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        content = json.loads(response.content)
        self.assertEqual(
            content, {"detail": "You do not have permission to perform this action."}
        )
        # Revoke should work
        data = {"id": update_user.id, "role": "student"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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
        data = {"id": update_user.id, "role": "moderator"}
        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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

        # Request with no filter returns the list of users but user5 that has no role
        # list ordered by public_username
        response = self.client.get("/api/v1/users/", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {"id": user3.id, "public_username": "Abba", "role": "moderator"},
                {"id": user2.id, "public_username": "Aurélie", "role": "student"},
                {"id": user4.id, "public_username": "Silvio", "role": "instructor"},
                {"id": user1.id, "public_username": "Thomas", "role": "student"},
            ],
        )

        response = self.client.get(
            "/api/v1/users/?role=student", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {"id": user2.id, "public_username": "Aurélie", "role": "student"},
                {"id": user1.id, "public_username": "Thomas", "role": "student"},
            ],
        )

        response = self.client.get(
            "/api/v1/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {"id": user3.id, "public_username": "Abba", "role": "moderator"},
            ],
        )

        response = self.client.get(
            "/api/v1/users/?role=instructor", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {"id": user4.id, "public_username": "Silvio", "role": "instructor"},
            ],
        )

    def test_list_moderators_only_moderator(self):
        """Creates users with roles student and moderator, these users should only
        be part of the list of moderators and not be part of the list of students"""
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        user2 = UserFactory(
            public_username="Aurélie", lti_consumer=api_user.lti_consumer
        )
        lti_context.sync_user_groups(user1, ["student", "moderator"])
        lti_context.sync_user_groups(user2, ["student", "moderator"])

        response = self.client.get(
            "/api/v1/users/?role=student", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, [])

        response = self.client.get(
            "/api/v1/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {"id": user2.id, "public_username": "Aurélie", "role": "moderator"},
                {"id": user1.id, "public_username": "Thomas", "role": "moderator"},
            ],
        )

    def test_list_users_no_moderator_if_no_student(self):
        """Controls that list of moderators only concerns users that are part of
        students group as well.
        """
        api_user, lti_context = self._login_authorized_user_to_manage_moderators()

        user1 = UserFactory(
            public_username="Thomas", lti_consumer=api_user.lti_consumer
        )
        user2 = UserFactory(
            public_username="Aurélie", lti_consumer=api_user.lti_consumer
        )
        lti_context.sync_user_groups(user1, ["moderator"])
        lti_context.sync_user_groups(user2, ["moderator"])

        response = self.client.get(
            "/api/v1/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, [])

        response = self.client.get(
            "/api/v1/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(content, [])

        response = self.client.get("/api/v1/users/", content_type="application/json")
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [
                {"id": user2.id, "public_username": "Aurélie", "role": None},
                {"id": user1.id, "public_username": "Thomas", "role": None},
            ],
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
            "/api/v1/users/?role=student", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content, [{"id": user1.id, "public_username": "Thomas", "role": "student"}]
        )
        # only active moderator is listed
        response = self.client.get(
            "/api/v1/users/?role=moderator", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content,
            [{"id": user2.id, "public_username": "Aurélie", "role": "moderator"}],
        )
        # only active instructor is listed
        response = self.client.get(
            "/api/v1/users/?role=instructor", content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        content = json.loads(response.content)
        self.assertEqual(
            content, [{"id": user5.id, "public_username": "Théo", "role": "instructor"}]
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

        data = {"role": "moderator", "public_username": "Salomé"}

        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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
        """If id in body of request api is different than the id in the url is ignored.
        Only the user targeted in the url is updated."""
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
        data = {"id": useless_user.id, "role": "moderator"}

        response = self.client.put(
            f"/api/v1/users/{update_user.id}/",
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
