"""Minimal Keycloak Admin API client used to provision users.

Talks to the realm's admin endpoints with a token from the master realm's
`admin-cli` public client. The token is cached in memory until it expires.
"""
import time
from typing import Optional

import requests

from keycloak._http import DEFAULT_TIMEOUT, safe_json, session
from keycloak.config import KeycloakConfig


class KeycloakAdminError(Exception):
  def __init__(self, status_code: int, body):
    self.status_code = status_code
    self.body = body
    super().__init__(f"Keycloak admin error {status_code}: {body}")


def _master_token_url() -> str:
  return f"{KeycloakConfig.base_url()}/realms/master/protocol/openid-connect/token"


class _AdminToken:
  value: Optional[str] = None
  expires_at: float = 0.0


def _admin_token() -> str:
  if _AdminToken.value and time.time() < _AdminToken.expires_at - 30:
    return _AdminToken.value

  try:
    resp = session.post(
      _master_token_url(),
      data={
        'grant_type': 'password',
        'client_id': 'admin-cli',
        'username': KeycloakConfig.ADMIN_USERNAME or 'admin',
        'password': KeycloakConfig.ADMIN_PASSWORD or 'admin',
      },
      timeout=DEFAULT_TIMEOUT,
    )
  except requests.RequestException as exc:
    raise KeycloakAdminError(502, {'error': 'keycloak_unreachable', 'detail': str(exc)}) from exc

  body = safe_json(resp)
  if not resp.ok or 'access_token' not in body:
    raise KeycloakAdminError(resp.status_code, body)

  _AdminToken.value = body['access_token']
  _AdminToken.expires_at = time.time() + int(body.get('expires_in', 60))
  return _AdminToken.value


def create_user(
  username: str,
  password: str,
  email: str = '',
  first_name: str = '',
  last_name: str = '',
) -> str:
  """Create a user in the configured realm. Returns the Keycloak user id."""
  payload = {
    'username': username,
    'enabled': True,
    'emailVerified': True,
    'email': email,
    'firstName': first_name,
    'lastName': last_name,
    'requiredActions': [],
    'credentials': [
      {'type': 'password', 'value': password, 'temporary': False},
    ],
  }

  try:
    resp = session.post(
      f"{KeycloakConfig.admin_url()}/users",
      json=payload,
      headers={'Authorization': f'Bearer {_admin_token()}'},
      timeout=DEFAULT_TIMEOUT,
    )
  except requests.RequestException as exc:
    raise KeycloakAdminError(502, {'error': 'keycloak_unreachable', 'detail': str(exc)}) from exc

  if not resp.ok:
    raise KeycloakAdminError(resp.status_code, safe_json(resp))

  location = resp.headers.get('Location', '')
  return location.rsplit('/', 1)[-1] if location else ''
