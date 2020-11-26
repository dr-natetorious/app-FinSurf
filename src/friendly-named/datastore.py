import os
import redis

class DataStore:
  """
  Represents a persistent storage device
  """
  def __init__(self, host:str, port:int):
    self.client = redis.Redis(
        host=host,
        port=port
    )

  def resolve_symbol(self, symbol) -> str:
    """
    Translates a stock symbol into a friendly name
    """
    value = self.client.get(symbol)
    if value is None or len(value) == 0:
      return symbol
    else:
      return value

  def set_symbol_translation(self,symbol:str,value:str) -> None:
    """
    Stores a stock symbols friendly name
    """
    self.client.set(symbol,value)
      