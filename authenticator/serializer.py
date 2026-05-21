from rest_framework import serializers


class AuthenticationSerializer(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField(write_only=True)
