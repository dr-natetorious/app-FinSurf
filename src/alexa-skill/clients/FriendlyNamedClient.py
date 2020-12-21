import os
import requests
import typing

class FriendlyNamedClient:
  """
  Represents a client for making values user-friendly
  """

  def __init__(self, base_url:str=None):
    if base_url is None:
      base_url = os.environ.get('FRIENDLY_NAME_API')
    if base_url is None:
      raise AssertionError("Unable to determine fn-api address")

    if base_url.endswith('/') == False:
      base_url += '/'
    
    self.base_url = base_url

  def resolve_symbol(self, symbol:str) -> str:
    address = "{base_url}{method}/{value}".format(
      base_url=self.base_url,
      method='s',
      value=symbol
    )

    return requests.get(address).text