"""
    Forum views
    ===========

    This module defines views provided by the ``forum`` application.

"""
from django.urls import reverse
from django.views.generic import UpdateView
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model("forum", "Forum")

PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)


class ForumRenameView(PermissionRequiredMixin, UpdateView):
    """ Allows the current user to update its forum profile. """

    model = Forum
    fields = ["name"]
    template_name = "forum/forum_rename.html"

    def get_success_url(self):
        """ Returns the success URL to redirect the user to. """
        return reverse(
            "forum:forum",
            kwargs={
                "pk": self.object.pk,
                "slug": self.object.slug,
            },
        )

    # pylint: disable=unused-argument
    def perform_permissions_check(self, user, obj, perms):
        """ Performs the permissions check. """
        return self.request.forum_permission_handler.can_rename_forum(obj, user)
