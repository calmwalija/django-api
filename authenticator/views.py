from django.contrib.auth.models import User
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from authenticator.serializer import AuthenticationSerializer, UserProfileSerializer


@extend_schema(tags=['Auth'])
class AuthenticationCreateAPIView(generics.CreateAPIView):
  serializer_class = AuthenticationSerializer
  permission_classes = [AllowAny]

  def create(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
      User.objects.create_user(
        username=serializer.validated_data["username"],
        password=serializer.validated_data["password"]
      )
      return Response(
        {"message": "User created successfully"},
        status=status.HTTP_201_CREATED
      )
    except Exception as e:
      return Response(
        {
          "error": str(e.args[-1]),
          "type": type(e).__name__
        },
        status=status.HTTP_400_BAD_REQUEST
      )


@extend_schema(tags=['Auth'])
class CurrentUserAPIView(generics.RetrieveAPIView):
  serializer_class = UserProfileSerializer
  permission_classes = [IsAuthenticated]

  def get_object(self):
    return self.request.user
