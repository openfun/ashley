"""
    Forum conversation signals
    ==========================
    This modules defines Django signals that can be triggered by the ``forum_conversation``
    application.
"""

import django.dispatch

topic_created = django.dispatch.Signal(
    providing_args=["topic", "user", "request", "response"]
)
topic_updated = django.dispatch.Signal(
    providing_args=["topic", "user", "request", "response"]
)
post_created = django.dispatch.Signal(
    providing_args=["post", "user", "request", "response"]
)
post_updated = django.dispatch.Signal(
    providing_args=["post", "user", "request", "response"]
)
