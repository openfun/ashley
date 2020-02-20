"""Factories for the ``lti_provider``."""

from factory.django import DjangoModelFactory

from . import models


class LTIConsumerFactory(DjangoModelFactory):
    """Factory to create LTI consumer."""

    class Meta:
        model = models.LTIConsumer
        django_get_or_create = ("slug",)


class LTIPassportFactory(DjangoModelFactory):
    """Factory to create LTI passport."""

    class Meta:
        model = models.LTIPassport
