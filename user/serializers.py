"""Serializers for the user app (User management)."""

from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from drf_spectacular.utils import extend_schema_field
from .models import User


def password_validation(value):
    """
    Validate password meets complexity requirements.
    - At least 8 characters long
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    # Password must be at least 8 characters long
    if len(value) < 8:
        raise serializers.ValidationError(
            "Password must be at least 8 characters long."
        )
    # Password must contain at least 1 uppercase letter
    if not any(char.isupper() for char in value):
        raise serializers.ValidationError(
            "Password must contain at least 1 uppercase letter."
        )
    # Password must contain at least 1 lowercase letter
    if not any(char.islower() for char in value):
        raise serializers.ValidationError(
            "Password must contain at least 1 lowercase letter."
        )
    # Password must contain at least 1 number
    if not any(char.isdigit() for char in value):
        raise serializers.ValidationError("Password must contain at least 1 number.")
    # Password must contain at least 1 special character
    special_characters = "¡!\"#$%&'()*+,-./:;<=>¿?@[\\]^_`{|}~"
    if not any(char in special_characters for char in value):
        raise serializers.ValidationError(
            "Password must contain at least 1 special character."
        )
    return value


class UserReadSerializer(serializers.ModelSerializer):
    """Serializer for reading users but not updating them nor creating them."""

    is_admin = serializers.SerializerMethodField()

    class Meta:
        """Meta class for UserReadSerializer with the required fields as read_only."""

        model = User
        fields = ("id", "email", "is_admin", "theme", "is_active")
        extra_kwargs = {
            "id": {"read_only": True},
            "email": {"read_only": True},
            "is_admin": {"read_only": True},
            "theme": {"read_only": True},
            "is_active": {"read_only": True},
        }

    @extend_schema_field(bool)
    def get_is_admin(self, obj):
        """Return True if user is in the admin group, False otherwise."""
        return obj.groups.filter(name="admin").exists()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating users."""

    is_admin = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        """
        Meta class with the required fields and password and is_active as write_only.
        """

        model = User
        fields = ("id", "email", "password", "is_admin", "theme", "is_active")
        extra_kwargs = {
            "email": {"required": True},
            "password": {"write_only": True},
            "is_active": {"write_only": True},
        }

    def create(self, validated_data):
        # Create user with hashed password
        password = validated_data.pop("password")
        is_admin = validated_data.pop("is_admin", None)
        user = User.objects.create_user(password=password, **validated_data)

        # Add user to admin group if is_admin is True
        if is_admin:
            admin_group = Group.objects.get(name="admin")
            user.groups.add(admin_group)

        return user

    def update(self, instance, validated_data):
        # Update password if it was included in the request
        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])

        # Update user groups if is_admin was included in the request
        if "is_admin" in validated_data:
            is_admin = validated_data.pop("is_admin", None)
            admin_group = Group.objects.get(name="admin")
            if is_admin:
                instance.groups.add(admin_group)
            else:
                instance.groups.remove(admin_group)

        return super(UserSerializer, self).update(instance, validated_data)

    def validate_password(self, value):
        """Validate password meets complexity requirements."""
        return password_validation(value)

    def validate_email(self, value):
        """Validate email is a tec.mx email."""
        if not value.endswith("@tec.mx"):
            raise serializers.ValidationError("Only tec.mx emails are allowed.")
        return value


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Serializer for requesting a password reset via email."""

    email = serializers.EmailField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for resetting a password with a token."""

    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def validate_password(self, value):
        """Validate password meets complexity requirements."""
        return password_validation(value)
