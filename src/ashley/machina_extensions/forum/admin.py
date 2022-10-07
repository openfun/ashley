"""
Import the admin classes from the django-machina's forum application
"""
import copy

from django.contrib import admin
from machina.apps.forum.admin import ForumAdmin as BaseForumAdmin
from machina.core.db.models import get_model

Forum = get_model("forum", "Forum")

admin.site.unregister(Forum)


class ForumAdmin(BaseForumAdmin):
    """The Forum model admin."""

    readonly_fields = ("lti_id",)
    search_fields = ("name", "lti_id")

    def get_fieldsets(self, request, obj=None):
        """Override fieldset to add the field lti_id"""
        fieldsets = copy.deepcopy(super().get_fieldsets(request, obj))
        fieldsets[0][1]["fields"] = (*fieldsets[0][1]["fields"], "lti_id")

        return fieldsets


admin.site.register(Forum, ForumAdmin)
