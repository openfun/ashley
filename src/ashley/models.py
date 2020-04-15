"""Declare the models related to Ashley ."""
import logging
from typing import List

from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.contrib.auth.models import Group
from django.db import models
from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from machina.core.db.models import model_factory

from lti_provider.models import LTIConsumer

logger = logging.getLogger(__name__)


class AbstractUser(DjangoAbstractUser):
    """Abstract user model for Ashley.

    The `username` and `password` fields are only used to authenticate
    django admins by django.contrib.auth.backends.ModelBackend.

    Non-admin user are authenticated via a LTI launch request, with the
    `lti_remote_identifier` and `lti_consumer` fields.

    Since the `username` field has a unique constraint, it is not used as
    public display name for users (2 users can have the same username if
    they come from distinct LTI consumers). The `public_username` field
    is used for this purpose.
    """

    lti_consumer = models.ForeignKey(LTIConsumer, on_delete=models.PROTECT, null=True)

    lti_remote_user_id = models.CharField(
        max_length=150,
        verbose_name=_("LTI remote user identifier"),
        help_text=_("Unique identifier for the user on the tool consumer"),
        blank=False,
    )

    public_username = models.CharField(
        max_length=150,
        verbose_name=_("Public username"),
        help_text=_("This username will be displayed with the user's posts"),
        blank=False,
    )

    def get_public_username(self):
        """Getter for the public username of the user."""
        return self.public_username

    def save(self, *args, **kwargs):
        if not self.public_username:
            self.public_username = self.username
        super().save(*args, **kwargs)

    class Meta:
        """Options for the ``AbstractUser`` model."""

        abstract = True
        app_label = "ashley"

        constraints = [
            models.UniqueConstraint(
                fields=["lti_consumer", "lti_remote_user_id"],
                name="ashleyuser_unique_consumer_remote_user_id",
            ),
        ]


# Default implementation of the AbstractUser, using django-machina's model factory
User = model_factory(AbstractUser)


class AbstractLTIContext(Model):
    """Abstract LTI Context model for Ashley."""

    GROUP_PREFIX = "cg"
    GROUP_DELIMITER = ":"

    lti_id = models.CharField(max_length=150, null=False, blank=False, db_index=True)

    lti_consumer = models.ForeignKey(
        LTIConsumer, on_delete=models.PROTECT, null=False, db_index=True
    )

    def get_base_group(self) -> Group:
        """
        Get the base (Django) Group for this LTI context.

        All LTI users authenticated within this LTI context should be in this group.
        """
        return self._get_or_create_group(self.base_group_name)

    @property
    def base_group_name(self) -> str:
        """
        Get the name of the base group.
        """
        return self.GROUP_DELIMITER.join([self.GROUP_PREFIX, str(self.id)])

    def get_role_groups(self, roles: List[str]) -> List[Group]:
        """
        Get the Django Groups corresponding to a list of LTI Context Roles

        All LTI users authenticated within this LTI context having these roles
        should be in these groups.
        """
        return list(map(self.get_role_group, roles))

    def get_role_group(self, role: str) -> Group:
        """
        Get the Django Group corresponding to a LTI Context Role

        All LTI user authenticated within this LTI context and having this role
        should be in this group.
        """
        group_name = self.GROUP_DELIMITER.join([self.base_group_name, "role", role])
        return self._get_or_create_group(group_name)

    @staticmethod
    def _get_or_create_group(group_name: str) -> Group:
        """
        Helper to get or create a Django Group by name
        """
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            logger.debug("Group %s created", group_name)
        return group

    def sync_user_groups(self, user, roles: List[str]) -> None:
        """
        Synchronize the group membership of a user for this LTI Context
        """

        current_groups = list(user.groups.filter(name__startswith=self.base_group_name))
        target_groups = self.get_role_groups(roles) + [self.get_base_group()]

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

    class Meta:
        """Options for the ``AbstractLTIContext`` model."""

        abstract = True
        app_label = "ashley"

        constraints = [
            models.UniqueConstraint(
                fields=["lti_consumer", "id"],
                name="lticontext_unique_consumer_context_id",
            ),
        ]


# Default implementation of the AbstractLTIContext model
LTIContext = model_factory(AbstractLTIContext)
