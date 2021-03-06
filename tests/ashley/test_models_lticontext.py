"""
Tests for the ashley.models.LTIContext model.
"""
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from machina.core.db.models import get_model

from ashley.factories import LTIConsumerFactory, LTIContextFactory, UserFactory

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

        # Create a LTI Consumer
        lti_consumer = LTIConsumerFactory()

        # Create 2 LTI Contexts for lti_consumer
        context1 = LTIContextFactory(lti_consumer=lti_consumer)
        context2 = LTIContextFactory(lti_consumer=lti_consumer)

        # Create an unrelated django group
        unrelated_group = Group.objects.create(name="unrelated_django_group")

        # Initialize a user with no group
        user = UserFactory(lti_consumer=lti_consumer)
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

        # Create another LTIConsumer
        lti_consumer2 = LTIConsumerFactory()

        # Create a LTI Context for lti_consumer2
        context3 = LTIContextFactory(lti_consumer=lti_consumer2)

        # Create a user for this LTI Context
        user2 = UserFactory(lti_consumer=lti_consumer2)

        # Check the PermissionDenied gets called as the user in not part of this LTIContext
        with self.assertRaises(PermissionDenied):
            context3.sync_user_groups(user, ["instructor"])

        # Check the PermissionDenied gets called as the user in not part of this LTIContext
        with self.assertRaises(PermissionDenied):
            context2.sync_user_groups(user2, [])

    def test_get_group_role_name(self):
        """get_group_role_name should return the name of the role with the specific pattern"""
        context = LTIContextFactory()

        # Ensure that the get_group_role_name generator respect a specific name pattern
        self.assertEqual(f"cg:{context.id}:role:", context.get_group_role_name(""))
        # Test with a actual group name label
        name_instructor_group = f"cg:{context.id}:role:instructor"
        self.assertEqual(
            name_instructor_group, context.get_group_role_name("instructor")
        )

    def test_get_user_roles(self):
        """get_user_roles should return the list of the roles names
        without the specific patterns cg:{context.id}:role: only the label
        of the roles
        """
        lti_consumer = LTIConsumerFactory()
        context = LTIContextFactory(lti_consumer=lti_consumer)

        # Create two users
        user = UserFactory(lti_consumer=lti_consumer)
        user2 = UserFactory(lti_consumer=lti_consumer)

        # Sync user groups in context with multiple roles
        context.sync_user_groups(user, ["role1", "role2"])
        # check that the list of roles is returned
        self.assertCountEqual(
            ["role1", "role2"],
            context.get_user_roles(user),
        )
        # add an extra group
        instructor_group = Group.objects.create(
            name=f"{context.base_group_name}:role:instructor"
        )
        user.groups.add(instructor_group)
        # check that the list of roles is returned
        self.assertCountEqual(
            ["role1", "role2", "instructor"],
            context.get_user_roles(user),
        )
        # check that group that are not roles get ignored
        other_group = Group.objects.create(name=f"{context.base_group_name}:other)")
        user2.groups.add(other_group)
        self.assertCountEqual(
            [],
            context.get_user_roles(user2),
        )
