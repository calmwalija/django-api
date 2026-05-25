from django.contrib.auth.models import User
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authenticator.serializer import AuthenticationSerializer, UserProfileSerializer
from keycloak.admin import KeycloakAdminError, create_user as keycloak_create_user


@extend_schema(tags=['Auth'])
class AuthenticationCreateAPIView(generics.CreateAPIView):
  """Register a user in Keycloak and mirror them locally as a Django User."""
  serializer_class = AuthenticationSerializer
  permission_classes = [AllowAny]

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    try:
      keycloak_user_id = keycloak_create_user(
        username=username,
        password=password,
        email=f"{username}@example.local",
        first_name=username,
        last_name='User',
      )
    except KeycloakAdminError as exc:
      return Response(
        {'error': 'keycloak_create_failed', 'detail': exc.body},
        status=exc.status_code if 400 <= exc.status_code < 600 else status.HTTP_502_BAD_GATEWAY,
      )

    try:
      User.objects.create_user(username=username, password=password)
    except IntegrityError:
      # Local mirror already exists; Keycloak is the source of truth, so continue.
      pass

    return Response(
      {
        'message': 'User created successfully',
        'username': username,
        'keycloak_user_id': keycloak_user_id,
      },
      status=status.HTTP_201_CREATED,
    )


@extend_schema(tags=['Auth'])
class CurrentUserAPIView(generics.RetrieveAPIView):
  serializer_class = UserProfileSerializer
  permission_classes = [IsAuthenticated]

  def get_object(self):
    return self.request.user
