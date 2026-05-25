from rest_framework import serializers


class KeycloakLoginRequestSerializer(serializers.Serializer):
  username = serializers.CharField()
  password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class KeycloakRefreshRequestSerializer(serializers.Serializer):
  refresh = serializers.CharField(write_only=True)


class KeycloakTokenResponseSerializer(serializers.Serializer):
  access_token = serializers.CharField()
  expires_in = serializers.IntegerField()
  refresh_token = serializers.CharField()
  refresh_expires_in = serializers.IntegerField()
  token_type = serializers.CharField()
  scope = serializers.CharField(required=False, allow_blank=True)
  session_state = serializers.CharField(required=False, allow_blank=True)
  not_before_policy = serializers.IntegerField(required=False, source='not-before-policy')
