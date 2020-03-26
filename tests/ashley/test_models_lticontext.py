"""
Tests for the ashley.models.LTIContext model.
"""
from django.contrib.auth.models import Group
from django.test import TestCase
from machina.core.db.models import get_model

from ashley.factories import LTIContextFactory, UserFactory

GroupForumPermission = get_model(  # pylint: disable=C0103
    "forum_permission", "GroupForumPermission"
)
LTIContext = get_model("ashley", "LTIContext")  # pylint: disable=C0103


class LTIContextTestCase(TestCase):
    """Test the utilities functions of the LTIContext model."""

    def test_group_generators(self):
        """Test utilities functions to generate django groups related to a LTIContext"""

        context = LTIContextFactory()
        # Create a django group (corresponding to the "student" role in the LTI context
        # we just created)
        initial_student_group = Group.objects.create(
            name=f"cg:{context.id}:role:student"
        )

        initial_group_count = Group.objects.count()

        # Ensure that the base group name generator respect a specific name pattern
        base_group_name = f"cg:{context.id}"
        self.assertEqual(base_group_name, context.base_group_name)

        base_group = context.get_base_group()
        # Ensure that the base group is created if it does not exist
        self.assertEqual(initial_group_count + 1, Group.objects.count())
        self.assertEqual(base_group_name, base_group.name)

        # Get the django group corresponding to the "student" role.
        role_group_student = context.get_role_group("student")
        # Ensure that the previously created group is returned and no new group is created
        self.assertEqual(initial_student_group, role_group_student)
        self.assertEqual(initial_group_count + 1, Group.objects.count())

        # Get the django group corresponding to the "instructor role
        role_group_instructor = context.get_role_group("instructor")
        # Ensure that the django group is created since it does not exist
        self.assertEqual(initial_group_count + 2, Group.objects.count())
        self.assertEqual(
            f"{base_group_name}:role:instructor", role_group_instructor.name
        )

    def test_sync_user_groups(self):
        """Test group synchronization"""

        # Create 2 LTI Contexts
        context1, context2 = LTIContextFactory.create_batch(2)

        # Create an unrelated django group
        unrelated_group = Group.objects.create(name="unrelated_django_group")

        # Initialize a user with no group
        user = UserFactory()
        self.assertEqual(0, user.groups.count())

        # Sync user groups in context1 with role "student"
        context1.sync_user_groups(user, ["student"])
        self.assertCountEqual(
            [context1.base_group_name, f"{context1.base_group_name}:role:student"],
            list(user.groups.values_list("name", flat=True)),
        )

        # Add the user to an unrelated django group
        user.groups.add(unrelated_group)

        # Sync user groups in context2 with multiple roles
        context2.sync_user_groups(user, ["role1", "role2"])
        self.assertCountEqual(
            [
                unrelated_group.name,
                context1.base_group_name,
                f"{context1.base_group_name}:role:student",
                context2.base_group_name,
                f"{context2.base_group_name}:role:role1",
                f"{context2.base_group_name}:role:role2",
            ],
            list(user.groups.values_list("name", flat=True)),
        )

        # Sync user groups in context 2 with another role
        context2.sync_user_groups(user, ["instructor"])
        self.assertCountEqual(
            [
                unrelated_group.name,
                context1.base_group_name,
                f"{context1.base_group_name}:role:student",
                context2.base_group_name,
                f"{context2.base_group_name}:role:instructor",
            ],
            list(user.groups.values_list("name", flat=True)),
        )

        # Sync user groups in context 1 with no role
        context1.sync_user_groups(user, [])
        self.assertCountEqual(
            [
                unrelated_group.name,
                context1.base_group_name,
                context2.base_group_name,
                f"{context2.base_group_name}:role:instructor",
            ],
            list(user.groups.values_list("name", flat=True)),
        )
