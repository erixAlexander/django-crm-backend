from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Note, Organization
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

# from django.forms.models import model_to_dict

# Use the custom User model
User = get_user_model()


class UserWithOrgSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True)  # Para input
    organization_display_name = serializers.SerializerMethodField()  # Para mostrar

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "password",
            "role",
            "organization_name",  # Input (no se muestra)
            "organization_display_name",  # Output (no se envía)
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "role": {"read_only": True},  # lo seteamos como 'admin' internamente
        }

    def get_organization_display_name(self, obj):
        return obj.organization.name if obj.organization else None

    def create(self, validated_data):
        org_name = validated_data.pop("organization_name")

        try:
            organization = Organization.objects.create(name=org_name)
        except IntegrityError:
            raise ValidationError(
                {"organization_name": "An organization with this name already exists."}
            )

        user = User.objects.create_user(
            **validated_data, role="admin", organization=organization
        )
        return user


class GetUsersInOrgSerializer(serializers.ModelSerializer):
    organization_name = serializers.SerializerMethodField()

    def get_organization_name(self, obj):
        return obj.organization.name if obj.organization else None

    class Meta:
        model = User
        fields = ["id", "username", "role", "organization_name", "email"]
        extra_kwargs = {"password": {"write_only": True}}


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role  # Add the role to the token payload
        token["organization"] = user.organization.name if user.organization else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role  # Include role in the response data
        data["username"] = self.user.username  # Optionally include username
        data["email"] = self.user.email  # Optionally include email
        data["organization"] = (
            self.user.organization.name if self.user.organization else None
        )
        return data


class CreateOrgUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        request = self.context["request"]
        current_user = request.user

        # Asociar el nuevo usuario a la misma organización del usuario autenticado
        new_user = User.objects.create_user(
            **validated_data,
            organization=current_user.organization,
            role="user"  # este tipo de usuarios no serán admin
        )
        return new_user


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "author"]


class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]  # add other editable fields as needed
        extra_kwargs = {
            "username": {"required": False},
            "email": {"required": False},
        }
