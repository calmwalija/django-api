"""Keycloak configuration loaded from environment variables.

Mirrors the structure used by the Kotlin server (KeycloakConfig.kt) so the
realm, client, and host values stay aligned across services.
"""
import os


class KeycloakConfig:
  PROTOCOL = os.environ.get('KEYCLOAK_PROTOCOL', 'https')
  HOST_URL = os.environ.get('KEYCLOAK_HOST_URL', 'localhost:8080')
  REALM_NAME = os.environ.get('KEYCLOAK_REALM', 'DjangoApi')
  CLIENT_ID = os.environ.get('KEYCLOAK_CLIENT_ID', 'djangoapi-client')

  CLIENT_SECRET = os.environ.get('KEYCLOAK_CLIENT_SECRET')
  ADMIN_USERNAME = os.environ.get('KEYCLOAK_ADMIN_USER')
  ADMIN_PASSWORD = os.environ.get('KEYCLOAK_ADMIN_PASSWORD')

  SCOPE = 'openid profile email'

  @classmethod
  def base_url(cls) -> str:
    return f"{cls.PROTOCOL}://{cls.HOST_URL}"

  @classmethod
  def issuer(cls) -> str:
    return f"{cls.base_url()}/realms/{cls.REALM_NAME}"

  @classmethod
  def jwks_url(cls) -> str:
    return f"{cls.issuer()}/protocol/openid-connect/certs"

  @classmethod
  def token_url(cls) -> str:
    return f"{cls.issuer()}/protocol/openid-connect/token"

  @classmethod
  def userinfo_url(cls) -> str:
    return f"{cls.issuer()}/protocol/openid-connect/userinfo"

  @classmethod
  def admin_url(cls) -> str:
    return f"{cls.base_url()}/admin/realms/{cls.REALM_NAME}"
