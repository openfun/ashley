"""
    Forum views
    ===========

    This module overrides views provided by the ``forum`` application.

"""
from django.db.models import F
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import UpdateView
from machina.apps.forum.views import ForumView as BaseForumView
from machina.apps.forum.views import IndexView as BaseIndexView
from machina.apps.forum_permission.shortcuts import remove_perm
from machina.apps.forum_permission.viewmixins import (
    PermissionRequiredMixin as BasePermissionRequiredMixin,
)
from machina.core.db.models import get_model
from machina.core.loading import get_class

from ashley.defaults import DEFAULT_FORUM_BASE_WRITE_PERMISSIONS

LTIContext = get_model("ashley", "LTIContext")
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
        query = urlencode(sorted(param.items()))
        return f"?{query}"

    def get_ordering_column(self):
        """From query url, retrieve the concerned field ordered on if any."""
        pfx, idx = self.get_ordering()
        if idx < len(self.list_display) and self.list_display[idx]:
            return pfx + self.list_display[idx]

        return self.get_default_index_order().get("col")


class IndexView(
    OrderByColumnMixin, BaseIndexView
):  # pylint: disable=too-many-ancestors
    """Displays the top-level forums."""

    # header columns
    list_display = ["name", "direct_topics_count", "direct_posts_count", "last_post_on"]

    def get_queryset(self):
        """Returns the list of items for this view ordered by column."""
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

    def get_context_data(self, **kwargs):
        """Returns the context data to provide to the template."""
        context = super().get_context_data(**kwargs)
        # Add information about the current lti_context
        try:
            context["course_locked"] = LTIContext.objects.get(
                id=self.request.forum_permission_handler.current_lti_context_id
            ).is_marked_locked
        except LTIContext.DoesNotExist:
            context["course_locked"] = False

        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # Add information about the current lti_context
        try:
            context["course_locked"] = LTIContext.objects.get(
                id=self.request.forum_permission_handler.current_lti_context_id
            ).is_marked_locked
        except LTIContext.DoesNotExist:
            context["course_locked"] = False

        return context


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


class ForumLockCourseView(PermissionRequiredMixin, UpdateView):
    """View to lock forums of the course."""

    model = Forum
    fields = ["lti_contexts"]
    template_name = "forum/forum_lock.html"

    def get_forums_list(self):
        """Returns the list of forums of this course"""
        return Forum.objects.filter(
            lti_contexts=self.get_object().lti_contexts.get(
                id=self.request.forum_permission_handler.current_lti_context_id
            )
        )

    def get_context_data(self, **kwargs):
        """Sends forums_list to the view"""
        context = super().get_context_data()
        context["forums_list"] = self.get_forums_list()
        return context

    def get_success_url(self):
        """Returns the success URL to redirect the user to."""
        return reverse("forum:index")

    # pylint: disable=unused-argument
    def perform_permissions_check(self, user, obj, perms):
        """
        Performs the permissions check. If forums is not part of current LTIContext
        access is refused.
        """
        if not obj.lti_contexts.filter(
            id=self.request.forum_permission_handler.current_lti_context_id
        ).exists():
            return False
        return self.request.forum_permission_handler.can_lock_course(obj, user)

    def post(self, request, *args, **kwargs):
        """
        We lock all forums of this course. Default group shouldn't have writing
        permissions anymore. The LTIContex will then be marked as blocked.
        """

        lti_context = self.get_object().lti_contexts.get(
            id=self.request.forum_permission_handler.current_lti_context_id
        )
        default_group = lti_context.get_base_group()

        # remove all permissions for each forum of this LTIContext
        for forum in self.get_forums_list():
            # pylint: disable=not-an-iterable
            for perm in DEFAULT_FORUM_BASE_WRITE_PERMISSIONS:
                remove_perm(perm, default_group, forum)

        # mark this course as locked
        lti_context.is_marked_locked = True
        lti_context.save()

        return HttpResponseRedirect(self.get_success_url())


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
