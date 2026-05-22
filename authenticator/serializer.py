from django.contrib.auth.models import User
from rest_framework import serializers


class AuthenticationSerializer(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = [
      'id',
      'username',
      'email',
      'first_name',
      'last_name',
      'is_active',
      'date_joined',
      'last_login',
    ]
    read_only_fields = fields
