"""Proxy views that exchange credentials / refresh tokens with Keycloak."""
import requests
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from keycloak._http import DEFAULT_TIMEOUT, safe_json, session
from keycloak.config import KeycloakConfig
from keycloak.serializers import (
  KeycloakLoginRequestSerializer,
  KeycloakRefreshRequestSerializer,
)


def _post_token(form: dict) -> tuple[int, dict]:
  try:
    resp = session.post(url=KeycloakConfig.token_url(), data=form, timeout=DEFAULT_TIMEOUT)
  except requests.RequestException as exc:
    return 502, {'error': 'keycloak_unreachable', 'detail': str(exc)}
  return resp.status_code, safe_json(resp)


class KeycloakLoginView(APIView):
  """Exchange username/password for a Keycloak access + refresh token."""
  permission_classes = [AllowAny]
  authentication_classes: list = []

  def post(self, request):
    serializer = KeycloakLoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code, body = _post_token({
      'grant_type': 'password',
      'client_id': KeycloakConfig.CLIENT_ID,
      'client_secret': KeycloakConfig.CLIENT_SECRET or '',
      'scope': KeycloakConfig.SCOPE,
      'username': serializer.validated_data['username'],
      'password': serializer.validated_data['password'],
    })
    return Response(body, status=code)


class KeycloakRefreshView(APIView):
  """Exchange a refresh token for a new access token."""
  permission_classes = [AllowAny]
  authentication_classes: list = []

  def post(self, request):
    serializer = KeycloakRefreshRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    code, body = _post_token({
      'grant_type': 'refresh_token',
      'client_id': KeycloakConfig.CLIENT_ID,
      'client_secret': KeycloakConfig.CLIENT_SECRET or '',
      'refresh_token': serializer.validated_data['refresh'],
    })
    return Response(body, status=code)
