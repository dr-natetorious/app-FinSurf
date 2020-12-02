#!/usr/bin/env python3
from ClientFactory import ClientFactory
from os import environ
from json import dumps
from logging import getLogger


logger = getLogger()
factory = ClientFactory()
tdclient = factory.create_client()

def process_all_instruments():  
  """
  Enumerates through all symbols
  """
  for prefix in range(65,91):
    prefix = chr(prefix)+'.*'

    instruments = tdclient.search_instruments(
      symbol=prefix,
      projection='symbol-regex')

    logger.debug('Query Prefix {} found {} instruments...'.format(
      prefix, len(instruments)))
    
    fetch_instrument_data(instruments.keys())

def fetch_instrument_data(symbols:list):
  """
  Fetches list of instruments fundamental data
  """
  for symbol in symbols:
    response = tdclient.search_instruments(
      symbol=symbol,
      projection='fundamental')
    
    send_service_data(
      serviceName='FUNDAMENTAL',
      contents=[response])

def send_service_data(serviceName:str, contents:list) -> None:
  if serviceName is None:
    raise ValueError('No serviceName provided')
  if len(contents) == 0:
    logger.warn('empty list given to send_service_data')
    return

  print(dumps({
    'data':[
      {
        'service':serviceName,
        'content':contents
      }
    ]
  }))

if __name__ == "__main__":
  process_all_instruments()
    