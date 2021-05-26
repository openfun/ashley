"""This module contains django widgets related to Ashley WYSIWYG editor """
import json

from django.forms.widgets import HiddenInput


class DraftEditor(HiddenInput):
    """Draft.js editor form field widget."""

    template_name = "widgets/editor.html"

    def get_context(self, name, value, attrs):
        """Add props to context."""
        context = super().get_context(name, value, attrs)
        # add to props mentions, forum, poster information and target input used in frontend
        context["widget"]["attrs"]["target"] = (
            context.get("widget").get("attrs").get("id")
        )
        context["widget"]["props"] = json.dumps(
            context.get("widget").get("attrs"), separators=(",", ":")
        )  # nosec
        return context


__all__ = ["DraftEditor"]
