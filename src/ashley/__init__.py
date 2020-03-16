"""Ashley is a django application that customizes and adds features to the django-machina forum."""


# pylint: disable=invalid-name
import os

default_app_config = "ashley.apps.AshleyConfig"

# Main Ashley template directory.
ASHLEY_MAIN_TEMPLATE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "templates",
)
