"""Declare the models related to Ashley ."""

from django.contrib.auth.models import AbstractUser as DjangoAbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from machina.core.db.models import model_factory

from lti_provider.models import LTIConsumer


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

    lti_consumer = models.ForeignKey(LTIConsumer, on_delete=models.CASCADE, null=True)

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
