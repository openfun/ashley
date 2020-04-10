"""This module contains custom decorators for draftjs_exporter."""
import logging

from draftjs_exporter.dom import DOM

logger = logging.getLogger(__name__)


def link(props):
    """
    Decorator for the `LINK` entity in Draft.js ContentState.

    `draftjs_exporter` does not provide a decorator for this kind of entity by
     default, so we have to define it to support links in forum posts.
    """
    title = props.get("title")
    href = props.get("url", "#")
    anchor_properties = {"href": href}

    if title is not None:
        anchor_properties["title"] = title

    return DOM.create_element("a", anchor_properties, props["children"])


def emoji(props):
    """
    Decorator for the `emoji` entity in Draft.js ContentState.

    This entity is added by the `draft-js-emoji-plugin` plugin.
    (https://www.draft-js-plugins.com/plugin/emoji)
    """
    return DOM.create_element("span", {"class": "emoji"}, props["children"])
