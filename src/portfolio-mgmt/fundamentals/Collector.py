#!/usr/bin/env python3
from ClientFactory import ClientFactory
from os import environ
from json import dumps
from logging import getLogger
from time import sleep
from ratelimitqueue import RateLimitQueue
import click

logger = getLogger()
factory = ClientFactory()
tdclient = factory.create_client()
max_calls = 60 # maximum is 120

def fetch_all_instruments(assetTypes:list):
  """
  Enumerates through all symbols
  """
  symbols = []
  filter_count=0
  for prefix in list(range(65,91)) + list(range(48,57)):
    prefix = '.*'+chr(prefix)

    instruments = tdclient.search_instruments(
      symbol=prefix,
      projection='symbol-regex')

    print('Query Prefix {} found {} instruments...'.format(
      prefix, len(instruments)))

    for symbol in instruments.keys():
      assetType = instruments[symbol]['assetType']
      if assetType in assetTypes:
        symbols.append(symbol)
      else:
        filter_count+=1

  print('Returning {} instruments with {} filtered...'.format(
    len(symbols), filter_count)
  )
  return symbols
    
def fetch_fundamental_data(symbols:list):
  """
  Fetches list of instruments fundamental data
  """
  queue = RateLimitQueue(calls=max_calls)
  [queue.put(x) for x in symbols]

  while queue.qsize() > 0:
    symbol = queue.get()
    
    # Submit the fundamental data
    response = tdclient.search_instruments(
      symbol=symbol,
      projection='fundamental')

    # Attempt to unpack the payload
    try:      
      content = response[symbol]['fundamental']
    except KeyError:
      continue

    send_service_data(
      serviceName='FUNDAMENTAL',
      contents=[content])

def fetch_quotes_data(symbols:list):
  """
  Fetches list of instruments fundamental data
  """
  queue = RateLimitQueue(calls=max_calls)
  [queue.put(x) for x in list(chunks(symbols,100)) ]

  while queue.qsize() > 0:
    instruments = queue.get()
    
    # Submit the fundamental data
    response = tdclient.get_quotes(
      instruments=instruments)
    
    # Attempt to unpack the payload
    try:
      contents = list(response.values())
    except KeyError:
      continue

    send_service_data(
      serviceName='QUOTE',
      contents=contents)

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

def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]