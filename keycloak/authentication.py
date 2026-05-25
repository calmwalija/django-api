"""DRF authentication backend that validates Keycloak-issued JWTs.

The bearer token is verified against the realm's JWKS (RS256). A local Django
User row is created on first sight so other parts of the project (FK on Patient,
DRF permissions) can use `request.user` as usual.
"""
import jwt
from django.contrib.auth import get_user_model
from jwt import PyJWKClient
from rest_framework import authentication, exceptions

from keycloak.config import KeycloakConfig

User = get_user_model()


class KeycloakAuthentication(authentication.BaseAuthentication):
  keyword = 'Bearer'

  _jwks_client: PyJWKClient | None = None

  @classmethod
  def _get_jwks_client(cls) -> PyJWKClient | None:
    if cls._jwks_client is None:
      cls._jwks_client = PyJWKClient(KeycloakConfig.jwks_url(), cache_keys=True)
    return cls._jwks_client

  def authenticate(self, request):
    header = authentication.get_authorization_header(request).split()
    if not header or header[0].lower() != self.keyword.lower().encode():
      return None
    if len(header) != 2:
      raise exceptions.AuthenticationFailed('Invalid Authorization header')

    token = header[1].decode()
    payload = self._decode(token)
    user = self._get_or_create_user(payload)
    return user, payload

  def authenticate_header(self, request):
    return f'{self.keyword} realm="{KeycloakConfig.REALM_NAME}"'

  def _decode(self, token: str) -> dict:
    try:
      signing_key = self._get_jwks_client().get_signing_key_from_jwt(token).key
      return jwt.decode(
        token,
        signing_key,
        algorithms=['RS256'],
        issuer=KeycloakConfig.issuer(),
        audience=KeycloakConfig.CLIENT_ID,
        options={'verify_aud': False},
      )
    except jwt.ExpiredSignatureError:
      raise exceptions.AuthenticationFailed('Token has expired')
    except jwt.InvalidTokenError as exc:
      raise exceptions.AuthenticationFailed(f'Invalid token: {exc}')

  @staticmethod
  def _get_or_create_user(payload: dict) -> User:
    username = (
      payload.get('preferred_username')
      or payload.get('email')
      or payload.get('sub')
    )
    if not username:
      raise exceptions.AuthenticationFailed('Token missing user claim')

    defaults = {
      'email': payload.get('email', '') or '',
      'first_name': payload.get('given_name', '') or '',
      'last_name': payload.get('family_name', '') or '',
    }
    user, _ = User.objects.get_or_create(username=username, defaults=defaults)
    return user
