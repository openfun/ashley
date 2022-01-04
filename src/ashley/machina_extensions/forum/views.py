"""
    Forum views
    ===========

    This module overrides views provided by the ``forum`` application.

"""
from django.db.models import F
from django.http import Http404
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import UpdateView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.apps.forum.views import IndexView as BaseIndexView
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

Forum = get_model("forum", "Forum")
ForumVisibilityContentTree = get_class("forum.visibility", "ForumVisibilityContentTree")

ORDER_VAR = "o"
PermissionRequiredMixin: BasePermissionRequiredMixin = get_class(
    "forum_permission.viewmixins", "PermissionRequiredMixin"
)


class OrderByColumnMixin:
    """Helper class to order by columns"""

    # default ordering
    default_ordering = "-last_post_on"

    def __init__(self):
        """Init called with default_ordering and list_display"""
        super().__init__()
        self.params = {}

    def get(self, request, *args, **kwargs):
        """Handles GET requests."""
        # collect the current params for the order by in request
        self.params = dict(request.GET.items())
        try:
            super_get = getattr(super(), "get")
            return super_get(request, *args, **kwargs)
        except AttributeError as exception:
            raise RuntimeError(
                "OrderByColumnMixin must be used as part of a "
                "multiple inheritance chain"
            ) from exception

    def get_default_index_order(self):
        """Utility to access index query column and column of default order with sign"""
        field = self.default_ordering.replace("-", "")
        sign = "-" if "-" in self.default_ordering else ""
        return {
            "index": f"{sign}{self.list_display.index(field)}",
            "col": self.default_ordering,
        }

    def get_context_data(self, **kwargs):
        """Returns the context data to provide to the template."""
        try:
            super_context = getattr(super(), "get_context_data")
            context = super_context(**kwargs)
        except AttributeError as exception:
            raise RuntimeError(
                "OrderByColumnMixin must be used as part of a "
                "multiple inheritance chain"
            ) from exception

        # add sort header links containing asc, desc orders
        context["header"] = list(self.result_headers())

        # used for pagination to keep the order, make sure it has expected value
        if self.request.GET.get(ORDER_VAR):
            pfx, idx = self.get_ordering()
            # if value is unexpected, order is ommited
            if f"{pfx}{idx}" == self.request.GET.get(ORDER_VAR):
                context["order"] = f"{ORDER_VAR}={pfx}{idx}"

        return context

    def get_ordering(self):
        """Gets order requested in url"""
        ordering = self.request.GET.get(
            ORDER_VAR, self.get_default_index_order().get("index")
        )
        try:
            _none, pfx, idx = ordering.rpartition("-")
            # returns default column if out of index order
            if int(idx) >= len(self.list_display):
                idx = self.get_default_index_order().get("col")
            return pfx, int(idx)
        except ValueError:
            # param exists but value is unexpected, use default order
            _none, pfx, idx = (
                self.get_default_index_order().get("index").rpartition("-")
            )
            return pfx, int(idx)

    def result_headers(self):
        """Builds each link and css class attribute for the header depending on current order"""
        pfx, idx = self.get_ordering()

        for index, _field_name in enumerate(self.list_display):
            new_order_type = "asc"
            div_classes = ""
            query_string = self.get_query_string({ORDER_VAR: "-" + str(index)})
            # Is it currently being sorted on?
            is_sorted = index == idx
            if is_sorted:
                order_type = "desc" if pfx == "-" else "asc"
                div_classes = f"sorted {order_type}ending"
                new_order_type = {"asc": "desc", "desc": "asc"}[order_type]
                query_string = self.get_query_string(
                    {ORDER_VAR: ("-" if pfx == "" else "") + str(index)}
                )

            yield {
                "sorted": is_sorted,
                "ascending": new_order_type == "desc",
                "url_order": query_string,
                "class_attrib": div_classes,
            }

    def get_query_string(self, new_params):
        """
        Build the query_string for this link keeping all the query params and replacing
        or adding new_params
        """
        param = {**self.params, **new_params}
        return "?%s" % urlencode(sorted(param.items()))

    def get_ordering_column(self):
        """From query url, retrieve the concerned field ordered on if any."""
        pfx, idx = self.get_ordering()
        if idx < len(self.list_display) and self.list_display[idx]:
            return pfx + self.list_display[idx]

        return self.get_default_index_order().get("col")


class IndexView(
    OrderByColumnMixin, BaseIndexView
):  # pylint: disable=too-many-ancestors
    """ Displays the top-level forums. """

    # header columns
    list_display = ["name", "direct_topics_count", "direct_posts_count", "last_post_on"]

    def get_queryset(self):
        """ Returns the list of items for this view ordered by column. """
        pfx, idx = self.get_ordering()
        f_query = F(self.list_display[idx])
        f_query_order_by = (
            f_query.desc(nulls_last=True)
            if pfx == "-"
            else f_query.asc(nulls_last=True)
        )

        return ForumVisibilityContentTree.from_forums(
            self.request.forum_permission_handler.forum_list_filter(
                Forum.objects.filter(archived=False).order_by(f_query_order_by),
                self.request.user,
            ),
        )


class ForumView(
    OrderByColumnMixin, BaseForumView
):  # pylint: disable=too-many-ancestors
    """Displays a forum and its topics."""

    # header columns
    list_display = ["subject", "posts_count", "views_count", "last_post_on"]

    def get_forum(self):
        """
        Returns the forum to consider and checks that it has not been
        archived.
        """
        forum = super().get_forum()
        if forum.archived:
            raise Http404()
        return forum

    def get_queryset(self):
        """Returns the list of items for this view ordered by asked param."""
        query = super().get_queryset()
        # Type of topic is kept as first order argument to keep sticky option
        return query.order_by("-type", self.get_ordering_column())


class ForumArchiveView(PermissionRequiredMixin, UpdateView):
    """Displays the form to archive a forum."""

    model = Forum
    fields = ["archived"]
    template_name = "forum/forum_archive.html"

    def get_success_url(self):
        """Returns the success URL to redirect the user to."""
        return reverse("forum:index")

    # pylint: disable=unused-argument
    def perform_permissions_check(self, user, obj, perms):
        """Performs the permissions check."""
        return self.request.forum_permission_handler.can_archive_forum(obj, user)

    def get_form_kwargs(self):
        """
        Ignores data posted by the user and forces the archiving of the forum.
        """
        kwargs = super().get_form_kwargs()
        kwargs.update({"data": {"archived": True}})
        return kwargs


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
