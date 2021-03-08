"""
    Forum views
    ===========

    This module defines views provided by the ``forum`` application.

"""
import logging

from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import UpdateView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

logger = logging.getLogger(__name__)

Forum = get_model("forum", "Forum")

ORDER_VAR = "o"
PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)


class ForumView(BaseForumView):  # pylint: disable=too-many-ancestors
    """Displays a forum and its topics."""

    # header columns
    list_display = ["subject", "posts_count", "views_count", "last_post_on"]

    def __init__(self, **kwargs):
        super().__init__()
        self.params = {}

    def get(self, request, **kwargs):
        """Handles GET requests."""
        # collect the current params for the order by in request
        self.params = dict(request.GET.items())
        response = super().get(request, **kwargs)
        return response

    def get_queryset(self):
        """Returns the list of items for this view ordered by asked params."""
        query = super().get_queryset()
        ordering = self.get_ordering()
        if ordering:
            query = query.order_by(*ordering)

        return query

    def get_context_data(self, **kwargs):
        """Returns the context data to provide to the template."""
        context = super().get_context_data(**kwargs)
        # add sort header links containing asc, desc, remove, toggle, primary links
        context["header"] = list(self.result_headers())
        return context

    def result_headers(self):
        """
        Generates the list column headers with appropriate links
        Based on admin list ordering in Django
        """
        ordering_field_columns = self.get_ordering_field_columns()
        logger.debug("Ordering field columns %s", ordering_field_columns)
        for i, _field_name in enumerate(self.list_display):
            order_type = ""
            new_order_type = "asc"
            div_classes = ""
            # Is it currently being sorted on?
            is_sorted = i in ordering_field_columns
            if is_sorted:
                order_type = ordering_field_columns.get(i).lower()
                div_classes = f"sorted {order_type}ending"
                new_order_type = {"asc": "desc", "desc": "asc"}[order_type]

            # build new ordering param
            o_list_primary = []  # URL for making this field the primary sort
            o_list_remove = []  # URL for removing this field from sort
            o_list_toggle = []  # URL for toggling order type for this field

            def make_qs_param(tri, key):
                return ("-" if tri == "desc" else "") + str(key)

            for j, tri in ordering_field_columns.items():
                if j == i:  # Same column
                    param = make_qs_param(new_order_type, j)
                    o_list_primary.insert(0, param)
                    o_list_toggle.append(param)
                else:
                    param = make_qs_param(tri, j)
                    o_list_primary.append(param)
                    o_list_toggle.append(param)
                    o_list_remove.append(param)

            if i not in ordering_field_columns:
                o_list_primary.insert(0, make_qs_param(new_order_type, i))

            yield {
                "sorted": is_sorted,
                "ascending": order_type == "asc",
                "sort_priority": list(ordering_field_columns).index(i) + 1
                if is_sorted
                else 0,
                "url_primary": self.get_query_string(
                    {ORDER_VAR: ".".join(o_list_primary)}
                ),
                "url_remove": self.get_query_string(
                    {ORDER_VAR: ".".join(o_list_remove)}
                ),
                "url_toggle": self.get_query_string(
                    {ORDER_VAR: ".".join(o_list_toggle)}
                ),
                "class_attrib": div_classes,
            }

    def get_ordering(self):
        """
        Returns the current ordering asc/desc and priority from params to build
        the order_by for this view.
        Based on admin list ordering in Django
        """
        params = self.params
        if ORDER_VAR in params:
            # Clear ordering and used params
            ordering = []
            order_params = params[ORDER_VAR].split(".")
            for prop in order_params:
                _none, pfx, idx = prop.rpartition("-")
                try:
                    idx = int(idx)
                    field_name = self.list_display[int(idx)]
                except (ValueError, IndexError):
                    continue
                order_field = field_name
                ordering.append(pfx + order_field)
            return ordering

        return []

    def get_ordering_field_columns(self):
        """
        Returns a dictionary of ordering field columns id from order params in
        request with value asc/desc.
        Based on admin list ordering in Django
        """
        ordering_fields = {}
        if ORDER_VAR in self.params:
            for param in self.params[ORDER_VAR].split("."):
                _none, pfx, idx = param.rpartition("-")
                try:
                    idx = int(idx)
                except ValueError:
                    continue  # skip it
                ordering_fields[idx] = "desc" if pfx == "-" else "asc"
        return ordering_fields

    def get_query_string(self, new_params=None, remove=None):
        """
        Build the query_string for this link.
        Based on admin list ordering in Django
        """
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []
        param = self.params.copy()
        for rem in remove:
            for key in list(param):
                if key.startswith(rem):
                    del param[key]
        for key, value in new_params.items():
            if value is None:
                if key in param:
                    del param[key]
            else:
                param[key] = value
        return "?%s" % urlencode(sorted(param.items()))


class ForumRenameView(PermissionRequiredMixin, UpdateView):
    """Allows the current user to update its forum profile."""

    model = Forum
    fields = ["name"]
    template_name = "forum/forum_rename.html"

    def get_success_url(self):
        """Returns the success URL to redirect the user to."""
        return reverse(
            "forum:forum",
            kwargs={
                "pk": self.object.pk,
                "slug": self.object.slug,
            },
        )

    # pylint: disable=unused-argument
    def perform_permissions_check(self, user, obj, perms):
        """Performs the permissions check."""
        return self.request.forum_permission_handler.can_rename_forum(obj, user)
