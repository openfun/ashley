"""
Template context processors
"""
import json

from django.conf import settings
from django.middleware.csrf import get_token


def site_metas(request):
    """Context processor to add all information required by Ashley templates and frontend."""
    if request.user.is_authenticated:
        return {
            "FRONTEND_CONTEXT": json.dumps(
                {
                    "context": {
                        "csrftoken": get_token(request),
                        "max_upload": settings.MAX_UPLOAD_FILE_MB,
                        "image_type": settings.IMAGE_TYPE_ALLOWED,
                    }
                }
            ),
        }
    return {}
