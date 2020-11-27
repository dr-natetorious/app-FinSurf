#!/usr/bin/env python3

from ClientFactory import ClientFactory
from os import environ
from json import dumps

factory = ClientFactory()
tdclient = factory.create_client()
streamer = tdclient.create_streaming_session()

def include_default_counters():
  """
  Include default symbols...
  """
  streamer.level_one_futures(symbols=['/ES','/VX','/GC','/CL','/ZB','/ZN','/NG','/HG','/ZS','/ZO','/ZW','/6E','/6B','/RTY'],fields=[0,1,2,3,4,8])
  streamer.account_activity()

def include_positions():
  """
  Find portfolio positions...
  """
  call_options = []
  put_options = []
  equities = ['$TICK','$UVOL','$DVOL','$ADVN','$DECN','$TRIN','$ADD']
  accounts = tdclient.get_accounts(fields=['positions'])
  print("Init for {} accounts".format(len(accounts)))
  for account in accounts:
    securitiesAccount = account['securitiesAccount']
    if 'positions' not in securitiesAccount:
      continue
    
    positions = securitiesAccount['positions']
    print('Found {} positions'.format(len(positions)))
    for position in positions:
      instrument = position['instrument']
      assetType = instrument['assetType']
      symbol = instrument['symbol']
      print(assetType +' '+symbol)
      
      if assetType == 'EQUITY':
        equities.append(symbol)
      if assetType == 'OPTION':
        equities.append(instrument['underlyingSymbol'])
        putCalls = instrument['putCall']
        if putCalls == 'CALL':
          call_options.append(symbol)
        else:
          put_options.append(symbol)
  
  equities = list(set(equities))
  print(equities)
  streamer.level_one_quotes(symbols=equities,fields= [0,1,2,3,4,5,6,7])
  streamer.news_headline(symbols=equities,fields=[0,3,5,9])

#include_default_counters()
include_positions()

streamer.write_flag=False
streamer.stream(print_to_console=True)
