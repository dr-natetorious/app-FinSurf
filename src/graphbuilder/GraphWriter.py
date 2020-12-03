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

      print('Get or creating {}'.format(symbol))
      symbol_v = self.g.V().has('instrument','symbol',symbol).fold().coalesce(
        __.unfold(),
        __.addV('instrument').property('symbol',symbol)).next()
      print('Complete {}'.format(symbol_v))
