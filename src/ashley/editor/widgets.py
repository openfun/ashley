"""This module contains django widgets related to Ashley WYSIWYG editor """
import json

from django.forms.widgets import HiddenInput
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _


class DraftEditor(HiddenInput):
    """Draft.js editor form field widget."""

    template_name = "widgets/editor.html"
    props = {
        "placeholder": _("Please enter your message here..."),
        "linkPlaceholder": _("Fill-in or paste your URL here and press enter"),
    }

    def __init__(self, attrs=None, props=None):
        """Allow optional extension of widget props in init."""
        super().__init__(attrs)
        if props:
            self.props.update(**props)

    def get_context(self, name, value, attrs):
        """Add props to context."""
        context = super().get_context(name, value, attrs)

        # add to props the list of active users for the current topic
        self.props["mentions"] = context.get("widget").get("attrs").get("mention_users")
        context["widget"]["props"] = mark_safe(json.dumps(self.props))  # nosec
        return context


__all__ = ["DraftEditor"]
