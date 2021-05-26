"""Serializer for ashley api."""
from django.contrib.auth import get_user_model
from machina.core.db.models import get_model
from rest_framework import serializers

from ashley.context_mixins import get_current_lti_session

User = get_user_model()
UploadImage = get_model("ashley", "UploadImage")


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "public_username", "roles"]
        read_only_fields = ["id", "public_username", "roles"]

    def get_roles(self, obj):
        """Describes the role of the user"""
        if obj.is_active:
            lti_context = get_current_lti_session(self.context.get("request"))
            return lti_context.get_user_roles(obj)

        return None


class UploadImageSerializer(serializers.ModelSerializer):
    """Serializer for Image Upload model."""

    class Meta:
        model = UploadImage
        fields = (
            "id",
            "file",
            "forum",
            "poster",
        )
        extra_kwargs = {"poster": {"required": False}}
