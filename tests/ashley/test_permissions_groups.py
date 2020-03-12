"""
Tests for the ashley.permissions.groups module.
"""
from django.contrib.auth.models import Group
from django.test import TestCase
from machina.apps.forum_permission.shortcuts import assign_perm
from machina.core.db.models import get_model

from ashley.factories import UserFactory
from ashley.machina_extensions.forum.factories import CourseForumFactory
from ashley.permissions import DEFAULT_GROUP_FORUM_PERMISSIONS
from ashley.permissions.groups import (
    GroupType,
    build_forum_group_name,
    get_or_create_group_with_default_permissions,
    sync_forum_user_groups,
)

GroupForumPermission = get_model(  # pylint: disable=C0103
    "forum_permission", "GroupForumPermission"
)


class GroupsTestCase(TestCase):
    """Test the utilities functions in the groups module."""

    def test_build_forum_group_name(self):
        """Test the group name generator."""

        self.assertEqual(
            "fg42__role__student", build_forum_group_name(42, GroupType.ROLE, "student")
        )

        self.assertEqual(
            "fg6__role__Instructor",
            build_forum_group_name(6, GroupType.ROLE, "Instructor"),
        )

        self.assertEqual(
            "fg1__cohort__MyCohort",
            build_forum_group_name(1, GroupType.COHORT, "MyCohort"),
        )

        with self.assertRaises(TypeError):
            build_forum_group_name(1, "InvalidGroupType", "MyCohort")

    def test_get_or_create_group_with_default_permissions(self):
        """Test the method get_or_create_group_with_default_permissions()."""
        # Create a forum
        forum = CourseForumFactory()

        # Create a group for this forum
        student_group_name = build_forum_group_name(forum.id, GroupType.ROLE, "student")
        student_group = Group.objects.create(name=student_group_name)
        student_group_permissions = [
            "can_see_forum",
            "can_read_forum",
            "can_start_new_topics",
        ]
        for perm in student_group_permissions:
            assign_perm(perm, student_group, forum, True)

        initial_group_count = Group.objects.count()

        # Test function with an existing group.
        tested_student_group = get_or_create_group_with_default_permissions(
            student_group_name, forum
        )
        self.assertEqual(student_group, tested_student_group)
        self.assertEqual(initial_group_count, Group.objects.count())
        group_permissions = GroupForumPermission.objects.filter(
            forum=forum, group=tested_student_group
        ).values_list("permission__codename", flat=True)
        self.assertEqual(student_group_permissions, list(group_permissions))

        # Test function with an unknown group
        moderator_group_name = build_forum_group_name(
            forum.id, GroupType.ROLE, "moderator"
        )
        moderator_group = get_or_create_group_with_default_permissions(
            moderator_group_name, forum
        )
        self.assertEqual(moderator_group_name, moderator_group.name)
        self.assertEqual(initial_group_count + 1, Group.objects.count())
        group_permissions = GroupForumPermission.objects.filter(
            forum=forum, group=moderator_group
        ).values_list("permission__codename", flat=True)
        self.assertEqual(DEFAULT_GROUP_FORUM_PERMISSIONS, list(group_permissions))

    def test_sync_forum_user_groups(self):
        """Test group synchronization."""

        user = UserFactory()

        forum1 = CourseForumFactory(lti_consumer=user.lti_consumer)
        forum2 = CourseForumFactory(lti_consumer=user.lti_consumer)

        initial_group1_name = build_forum_group_name(
            forum1.id, GroupType.ROLE, "student"
        )
        initial_group2_name = build_forum_group_name(
            forum1.id, GroupType.COHORT, "MyInitialCohort"
        )
        initial_group3_name = build_forum_group_name(
            forum2.id, GroupType.ROLE, "instructor"
        )
        initial_group4_name = "another_group"

        initial_group1 = Group.objects.create(name=initial_group1_name)
        initial_group2 = Group.objects.create(name=initial_group2_name)
        initial_group3 = Group.objects.create(name=initial_group3_name)
        initial_group4 = Group.objects.create(name=initial_group4_name)

        user.groups.set(
            [initial_group1, initial_group2, initial_group3, initial_group4]
        )
        self.assertCountEqual(
            [
                initial_group1_name,
                initial_group2_name,
                initial_group3_name,
                initial_group4_name,
            ],
            list(user.groups.values_list("name", flat=True)),
        )

        new_forum1_group1_name = build_forum_group_name(
            forum1.id, GroupType.ROLE, "moderator"
        )
        new_forum1_group2_name = build_forum_group_name(
            forum1.id, GroupType.COHORT, "MyNewCohort"
        )
        sync_forum_user_groups(
            user, forum1, [new_forum1_group1_name, new_forum1_group2_name]
        )

        self.assertCountEqual(
            [
                new_forum1_group1_name,
                new_forum1_group2_name,
                initial_group3_name,
                initial_group4_name,
            ],
            list(user.groups.values_list("name", flat=True)),
        )
