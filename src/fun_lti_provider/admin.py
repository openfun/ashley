"""Admin of the fun_lti_provider application"""

from django.contrib import admin

from .models import LTIConsumer, LTIPassport


@admin.register(LTIConsumer)
class LTIConsumerAdmin(admin.ModelAdmin):
    """Admin class for the LTIConsumer model."""

    list_display = (
        "slug",
        "title",
    )


@admin.register(LTIPassport)
class LTIPassportAdmin(admin.ModelAdmin):
    """Admin class for the LTIPassport model."""

    list_display = (
        "title",
        "oauth_consumer_key",
        "is_enabled",
    )

    readonly_fields = [
        "oauth_consumer_key",
        "shared_secret",
    ]
