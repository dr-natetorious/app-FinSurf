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
    if 'data' in message:
      for child in message['data']:
        self.write_td_stream_message(child)
      return
    
    if 'service' in message:
      serviceName = message['service']
      if 'content' in message:
        logger.warn('expected content node missing')
        continue

      if serviceName == 'QUOTE':
        self.__write_tdquote_message(message)
      if serviceName == 'FUNDAMENTAL':
        self.__write_tdfundamental_message(message)
  
  def __write_tdfundamental_message(self, message:dict) -> None:
    for content in message['content']:
      symbol = content['symbol']
      v = self.g.V().has('quote','key',symbol)
      
      if v == None:
        v = self.g.addV('fundamental').property('key',symbol)

    data = content[symbol]['fundamental']
    for key in data.keys()
      v = v.property(key, data[key])

    v.next()

  def __write_tdquote_message(self, message:dict) -> None:
    if 'content' in message:
      logger.warn('expected content node missing')
      return

    timestamp = message['timestamp']
    for content  in message['content']:
      key = content['key']
      v = self.g.V().has('quote','key',key)

      if v == None:
        v = self.g.addV('quote').property('key',key)     
      
      # Set additional properties
      v = v.property('timestamp',timestamp)
      if '1' in content:
        v = v.property('bid',content['1'])
      if '2' in content:
        v = v.property('ask',content['2'])
      if '3' in content:
        v = v.property('last',content['3'])
      if '8' in content:
        v = v.property('volume',content['3'])

      v.next()
