"""
This module contains additional group related features for Ashley.

A Ashley user belongs to (django) groups that reflect his group membership on
the Consumer site.

Let's take for example a user "Toto" who wants to browse the forum related to the
course "Mathematics101" on the "MyLMS" Consumer site. "Toto" has the role "Student"
on this course. And "Toto" belongs the the cohort "my_cohort" on this course.

Instead of creating a custom Group model (that implies to rewrite the PermissionMixin
on the AbstractUser and all group related features in django-machina) to store these
information, we'll generate a group name using the following schema :

{forum_id}__{group_type}__{name}

The Forum model contains the consumer site and the course id (LTI context id), so we
can use its id to generate the group name. Also, this will prevent exceeding the max
length of the group name.

To get back to our example, lets assume that the forum with id 42 correspond to
the course "Mathematics101" on "MyLMS".

Then, the user "Toto" will belong to the following groups :

 - 42__role__student
 - 42__cohort__my_cohort

"""

import logging
from enum import Enum
from typing import List

from django.contrib.auth.models import Group
from machina.apps.forum_permission.shortcuts import assign_perm

from ashley.machina_extensions.forum.models import AbstractForum
from ashley.models import AbstractUser
from ashley.permissions import (
    DEFAULT_ADMIN_GROUP_FORUM_PERMISSIONS,
    DEFAULT_GROUP_FORUM_PERMISSIONS,
    DEFAULT_INSTRUCTOR_GROUP_FORUM_PERMISSIONS,
)

logger = logging.getLogger("ashley")

GROUP_DELIMITER = "__"
GROUP_PREFIX = "fg"


class GroupType(Enum):
    """
    Declaration of the supported group types.
    """

    COHORT = "cohort"
    ROLE = "role"


def build_forum_group_name(forum_id: int, group_type: GroupType, name: str) -> str:
    """Build a course group name, based on a forum_id, a group type and a name."""
    if not isinstance(group_type, GroupType):
        raise TypeError
    return f"{GROUP_PREFIX}{forum_id}{GROUP_DELIMITER}{group_type.value}{GROUP_DELIMITER}{name}"


def get_or_create_group_with_default_permissions(
    group_name: str, forum: AbstractForum
) -> Group:
    """
    Fetch a Group by name. If it does not exist, it is created and default
    permissions are assigned.
    """
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        permissions_to_assign = get_group_default_permissions(group_name, forum)
        for perm in permissions_to_assign:
            assign_perm(perm, group, forum, True)
    return group


def get_group_default_permissions(group_name: str, forum: AbstractForum) -> List[str]:
    """
    Get the default permissions for a group.
    It detects special groups (Administrator and Instructor roles) to grant
    them additional permissions.
    """
    if not group_name.startswith(f"{GROUP_PREFIX}{forum.id}{GROUP_DELIMITER}"):
        return []
    if group_name.endswith(f"{GroupType.ROLE.value}{GROUP_DELIMITER}administrator"):
        return DEFAULT_ADMIN_GROUP_FORUM_PERMISSIONS
    if group_name.endswith(f"{GroupType.ROLE.value}{GROUP_DELIMITER}instructor"):
        return DEFAULT_INSTRUCTOR_GROUP_FORUM_PERMISSIONS
    return DEFAULT_GROUP_FORUM_PERMISSIONS


def sync_forum_user_groups(
    user: AbstractUser, course_forum: AbstractForum, group_names: List[str]
) -> None:
    """
    Synchronize the group membership of a user for a given forum with
    with the given group list. If a groups does not exist, it is created.
    """
    current_groups = list(
        user.groups.filter(
            name__startswith=f"{GROUP_PREFIX}{course_forum.id}{GROUP_DELIMITER}"
        )
    )

    target_groups = list(
        map(
            lambda group_name: get_or_create_group_with_default_permissions(
                group_name, course_forum
            ),
            group_names,
        )
    )

    logger.debug("Current groups : %s", current_groups)
    logger.debug("Target groups : %s", target_groups)

    # Remove groups if necessary
    for group in current_groups:
        if group not in target_groups:
            logger.debug("Removing user %s from group %s", user, group)
            user.groups.remove(group)

    # Add group if necessary
    for group in target_groups:
        if group not in current_groups:
            logger.debug("Add user %s to group %s", user, group)
            user.groups.add(group)
