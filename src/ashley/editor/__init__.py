"""
This package contains utilities for Ashley's WYSIWYG editor.
"""

import json
import logging

from draftjs_exporter.html import HTML

from ..defaults import DRAFTJS_EXPORTER_CONFIG

logger = logging.getLogger(__name__)

DRAFTJS_EXPORTER = HTML(DRAFTJS_EXPORTER_CONFIG)


def draftjs_renderer(content: str) -> str:
    """Convert a Draft.js JSON state into HTML"""
    try:
        return str(DRAFTJS_EXPORTER.render(json.loads(content)))
    except json.JSONDecodeError as err:
        logger.warning("Unable to render content : %s (content : [%s])", err, content)
    return ""
