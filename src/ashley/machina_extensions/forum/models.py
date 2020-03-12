"""Declare the models related to Ashley ."""

from django.db import models
from machina.apps.forum.abstract_models import AbstractForum as MachinaAbstractForum
from machina.core.db.models import model_factory

from lti_provider.models import LTIConsumer


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

    lti_consumer = models.ForeignKey(
        LTIConsumer, on_delete=models.SET_NULL, null=True, db_index=True
    )

    lti_context = models.CharField(max_length=150, null=True, blank=True, db_index=True)

    class Meta(MachinaAbstractForum.Meta):
        abstract = True


Forum = model_factory(AbstractForum)

from machina.apps.forum.abstract_models import *  # noqa isort:skip
