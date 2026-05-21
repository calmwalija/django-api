from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from authenticator.serializer import AuthenticationSerializer


# Create your views here.


class AuthenticationCreateAPIView(generics.CreateAPIView):
  serializer_class = AuthenticationSerializer

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


class AuthenticationRetrieveAPIView(generics.RetrieveAPIView):
  serializer_class = AuthenticationSerializer
  queryset = User.objects.all()
  lookup_field = "username"
