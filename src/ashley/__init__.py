"""
Ashley is a self-hosted alternative discussion forum for OpenEdx.

It is based on django-machina, so this app contains domain specific features
and customization.
"""

import os

# Ashley template directory.
ASHLEY_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates/ashley",
)
