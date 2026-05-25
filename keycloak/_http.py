"""Shared HTTP session for Keycloak calls.

A single connection pool is reused across login, refresh, and admin operations,
which keeps latency low when Keycloak handles many auth requests.
"""
import requests

DEFAULT_TIMEOUT = 10

session = requests.Session()


def safe_json(resp: requests.Response) -> dict:
  try:
    return resp.json() if resp.content else {}
  except ValueError:
    return {'error': resp.text or resp.reason}
