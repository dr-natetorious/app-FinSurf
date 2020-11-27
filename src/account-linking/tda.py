from td.client import TDClient
import urllib
import time
from json import dumps
from datetime import datetime
from os import environ

class AccountLinkingClient:
  """
  Represents a client for linking Ameritrade 
  """
  def __init__(self, client_id:str=None, redirect_uri:str=None) -> None:
    # Default the values if not provided.
    if client_id is None:    
      client_id = environ.get('TDA_CLIENT_ID')
    if redirect_uri is None:
      redirect_uri = environ.get('TDA_REDIRECT_URI')

    if client_id is None:
      raise AssertionError('client_id is not available') 

    if redirect_uri is None:
      raise AssertionError('redirect_uri is not available')

    self.client_id=client_id
    self.redirect_uri=redirect_uri
    self.client = TDClient(client_id=client_id, redirect_uri=redirect_uri)

  def create_credentials_from_urlcode(self, url_code:str) -> dict:
    """
    Creates the contents for a td_state.json credential document.
    """
    if url_code is None:
      raise AssertionError('url_code is not available')

    client = TDClient(client_id=self.client_id, redirect_uri=self.redirect_uri)

    # Define the parameters of our access token post.
    data = {
      'grant_type': 'authorization_code',
      'client_id': self.client_id + '@AMER.OAUTHAP',
      'access_type': 'offline',
      'code': url_code,
      'redirect_uri': self.redirect_uri
    }

    # Translate the code into a access token
    token_dict = client._make_request(
      method='post',
      endpoint=client.config['token_endpoint'],
      mode='form',
      data=data
    )

    if token_dict is None:
      raise AssertionError('Unable to translate the code to token')

    # Compute the additional expected values
    access_token_expire = time.time() + int(token_dict['expires_in'])
    refresh_token_expire = time.time() + int(token_dict['refresh_token_expires_in'])
    token_dict['access_token_expires_at'] = access_token_expire
    token_dict['refresh_token_expires_at'] = refresh_token_expire
    token_dict['logged_in'] = True
    token_dict['access_token_expires_at_date'] = datetime.utcfromtimestamp(access_token_expire).isoformat()
    token_dict['refresh_token_expires_at_date'] = datetime.utcfromtimestamp(refresh_token_expire).isoformat()
    
    return token_dict

if __name__ == '__main__':
  linker = AccountLinkingClient()

  url_code ='7V95POSq+nQDhgPWc+Webkkab2LNZaP2IsuL+1Lfd3B5sWpwUl5itJk/BqBZA6ubH6WKvisiTimeIDyKl/52WMhWov8aITaB+zik8ryhGOkI8K5v4IoIwxK9f/nRlXLEO0UWQeQlH8Zv/K/Of6bng6VWzyAbMrbOaIPK/V4zPHjgQpsDPQJHtiqHHWh0Bk2OB/gXyH+ljdrJg2/K8bRFPLOn3xvvbUD/RXc3/Q7CkFbnlh3VatiZbC6xiEA6v+qZAc2TjHySP+ucYSoWyLWxXabz8Zvv60WX9Zghdz6GYctm/kG7fv7ssDbUUOvd3ybiT6ZZQ+wYKQJRa1AuIT9NF+JnMxyIhmaivlpQ4K9phi8jmc0BeSO+dX5iwap1ZjZQnjIx/tvokQ2mgdbSR/RV1zarmMgeOcHKbGKLjtlb6AmFsUdX7OwG8dicL3G100MQuG4LYrgoVi/JHHvl+VH76BJFSFYz3vG7Yc24/iHTMyfpp0L671irgTHz2lDiBV2B/QZfQVpi+pUhW9tVCEgY7FSW3YDn1+Dt6xEG3GTYB6rsUUiR/a9iChVNsMg6QD3uAUp676w6iEOk2feE7b4lEao3MoGGQeFFA3atABjjx/QmQbfEiBGHNhyfjJ7MckL9FHTiKvito4tJIIz9soScKCCkWWcm6S2PexsZjBPW3UE6dxpusBh3K3ywG6yiNm6tQq+GIbYpVDeZulDt0PjPRn8738CoRA7oMUykzICI1KSsnKdNo98nHqlZwEiAGupAQZNKQJw5NVbAZFZG8V/rc49PVPDK/cuxdkNdjg4k8FFl3YJdu8AITIVj+08aSCZ0ft+CsVvWkGWwgEJFOnitema7CMTFDJAcHnwuhq134kWo7ci9r20bOMcWfob7lzwRkcTiCMV+EHQ=212FD3x19z9sWBHDJACbC00B75E'
  creds = linker.create_credentials_from_urlcode(url_code=url_code)

  with open('./creds.json','w+') as f:
    f.write(dumps(creds))

  session = TDClient(
    client_id=linker.client_id,
    redirect_uri=linker.redirect_uri,
    credentials_path='./creds.json')
  quotes = session.get_quotes(instruments=['MSFT','AMZN'])
  print(quotes)
