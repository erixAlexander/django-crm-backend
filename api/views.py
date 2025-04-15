from django.shortcuts import render
from .models import User, Note, Organization
from rest_framework import generics
from .serializers import (
    GetUsersInOrgSerializer,
    NoteSerializer,
    MyTokenObtainPairSerializer,
    UserWithOrgSerializer,
    CreateOrgUserSerializer,
    UpdateUserSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied


class RegisterAdminWithOrgView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserWithOrgSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Step 1: Validate and save user + org
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Create tokens
        refresh = RefreshToken.for_user(user)

        # Customize the access token payload
        access_token = refresh.access_token
        access_token["role"] = user.role
        access_token["organization"] = (
            user.organization.name if user.organization else None
        )

        # Step 3: Return tokens and user info
        return Response(
            {
                "refresh": str(refresh),
                "access": str(access_token),  # now contains role & org
                "username": user.username,
                "role": user.role,
                "organization": user.organization.name,
            },
            status=status.HTTP_201_CREATED,
        )


# User Registration View (No change, still working as before)
class CreateOrgUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateOrgUserSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role != "admin":
            return Response(
                {"error": "Only admins can create users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        created_user = serializer.save()

        return Response(
            {
                "username": created_user.username,
                "email": created_user.email,
                "organization": created_user.organization.name,
            },
            status=status.HTTP_201_CREATED,
        )


# Custom Token View to include the role in the JWT
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# Note Views (No changes here, just showing for completeness)
class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Note.objects.filter(author=user)

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class NoteDeleteView(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, serializer):
        user = self.request.user
        return Note.objects.filter(author=user)


class GetMyOrgUsersView(generics.ListAPIView):
    serializer_class = GetUsersInOrgSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Safely get the organization and username from the authenticated user
        user = self.request.user
        if user.role != "admin":
            return Response(
                {"error": "Only admins can create users."},
                status=status.HTTP_403_FORBIDDEN,
            )
        organization = user.organization

        if not organization:
            # Return an empty queryset if the user has no associated organization
            return User.objects.none()

        # Filter users by organization ID and exclude the requesting user
        return User.objects.filter(organization=organization.id)


class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permision_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != "admin":
            return Response(
                {"error": "Only admins can delete users."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user_id_to_delete = kwargs.get("pk")
        try:
            user_to_delete = User.objects.get(username=user_id_to_delete)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if user_to_delete.organization != user.organization:
            return Response(
                {"error": "You can only delete users in your organization."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Prevenir que un admin se elimine a sí mismo (opcional pero recomendable)
        if user.id == user_to_delete.id:
            return Response(
                {"error": "You cannot delete yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_to_delete.delete()
        return Response(
            {"message": "User deleted successfully."},
            status=status.HTTP_204_NO_CONTENT,
        )


class UpdateOrgUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get username from the URL (pk is actually the username here)
        username = self.kwargs["pk"]
        user_to_update = get_object_or_404(User, username=username)

        requesting_user = self.request.user

        # Authorization checks
        if requesting_user.role != "admin":
            raise PermissionDenied("Only admins can update users.")

        if user_to_update.organization != requesting_user.organization:
            raise PermissionDenied("You can only update users in your organization.")

        if user_to_update == requesting_user:
            raise PermissionDenied("You cannot update your own data here.")

        return user_to_update

    def update(self, request, *args, **kwargs):
        print("📦 Incoming request data:", request.data)
        return super().update(request, *args, **kwargs)
