"""Ashley is a django application that customizes and adds features to the django-machina forum."""


# pylint: disable=invalid-name
import os

default_app_config = "ashley.apps.AshleyConfig"

# Main Ashley template directory.
ASHLEY_MAIN_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "templates",
)

# Name of the session entry containing the current LTI context ID
SESSION_LTI_CONTEXT_ID = "ltictx"
