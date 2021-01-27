"""Middleware declaration for the forum_permission machina app"""

from machina.apps.forum_permission.middleware import (
    ForumPermissionMiddleware as BaseForumPermissionMiddleware,
)

from ashley import SESSION_LTI_CONTEXT_ID


class ForumPermissionMiddleware(BaseForumPermissionMiddleware):
    """
    Django Machina's ForumPermissionMiddleware attaches an instance of the
    PermissionHandler to each request.

    We override it to store the current LTI context ID (that is stored in
    session), when it is available, in the permission handler.

    Since machina permission checking functions are not aware of the request
    object, this allows to use this information for permission checking.
    """

    def process_request(self, request):
        super().process_request(request)

        if request.user.is_authenticated:
            current_lti_context_id = request.session.get(SESSION_LTI_CONTEXT_ID)
            if current_lti_context_id:
                request.forum_permission_handler.current_lti_context_id = (
                    current_lti_context_id
                )
