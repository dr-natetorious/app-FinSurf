from gremlin_python import statics
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from logging import getLogger
from typing import List
from datetime import datetime
from os import environ

logger = getLogger()

class GraphWriter:

  def __init__(self,neptune_endpoint:str=None)->None:
    if neptune_endpoint is None:
      neptune_endpoint = environ.get('NEPTUNE_ENDPOINT')
      
    if not neptune_endpoint.startswith('wss://'):
      neptune_endpoint = 'wss://'+neptune_endpoint
    if not neptune_endpoint.endswith('/gremlin'):
      neptune_endpoint += ':8182/gremlin'

    self.graph = Graph()
    self.connection = DriverRemoteConnection(neptune_endpoint,'g')
    self.g = self.graph.traversal().withRemote(self.connection)

  def write_td_stream_message(self,message:dict):
    payload:dict = message['data'][0]
    serviceName:str = payload['service']
    contents:list = payload['content']

    if serviceName == 'QUOTE':
      self.write_quote(contents)
      return
    
    print('Error: Unknown serviceName - {}'.format(serviceName))
  
  def write_quote(self, contents:list):
    for content in contents:
      symbol = content['symbol']
      exchangeName = content['exchangeName']
      trade_time = datetime.utcfromtimestamp(content['tradeTimeInLong'] / 1000)
      trade_session = "{:04d}-{:02d}-{:02d}".format(
        trade_time.year,
        trade_time.month,
        trade_time.day)

      print('Processing {}'.format(symbol))
      symbol_v = self.get_or_create_vertice('instrument','symbol',symbol)      
      exchange_v = self.get_or_create_vertice('exchange','name',exchangeName)
      self.get_or_create_edge(exchange_v,symbol_v,'transacts')

      trading_session_v = self.get_or_create_vertice('trading_session','session',trade_session)
      self.get_or_create_edge(symbol_v,trading_session_v,'trades-during')

  def get_or_create_vertice(self,label:str,name:str,value:str):
    return self.g.V().has(label,name,value).fold().coalesce(
        __.unfold(),
        __.addV(label).property(name,value)).next()

  def get_or_create_edge(self,v1,v2,label:str):
    return self.g.V(v1).as_('v1').V(v2).coalesce(
      __.inE(label).where(
        __.outV().as_('v1')
      ),
      __.addE(label).from_('v1'))
