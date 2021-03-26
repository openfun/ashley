"""Serializer for ashley api."""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from ashley.context_mixins import get_current_lti_session

User = get_user_model()


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
