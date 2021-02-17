"""Declare the models related to Ashley ."""
import uuid

from django.db import models
from machina.apps.forum.abstract_models import AbstractForum as MachinaAbstractForum
from machina.core.db.models import get_model, model_factory

LTIContext = get_model("ashley", "LTIContext")  # pylint: disable=C0103


class AbstractForum(MachinaAbstractForum):
    """
    Forum model for Ashley.

    It is based on django-machina's Forum model and adds fields to be able to
    map a LTI request to a forum.
    """

    # pylint: disable=all
    # Pylint is disabled because it crashes while testing Foreign keys declared in the
    # django-machina's parent abstract model. This is a known issue in pylint-django with
    # foreign keys models referenced by their name.
    # (See https://github.com/PyCQA/pylint-django#known-issues )
    lti_id = models.UUIDField(
        null=False, default=uuid.uuid4, editable=False, unique=False, db_index=True
    )

    lti_contexts = models.ManyToManyField(LTIContext)

    class Meta(MachinaAbstractForum.Meta):
        abstract = True


Forum = model_factory(AbstractForum)

from machina.apps.forum.abstract_models import *  # noqa isort:skip
