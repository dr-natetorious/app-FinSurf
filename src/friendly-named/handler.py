from json import dumps,loads
from datastore import DataStore
import redis
import logging
import os

logger = logging.getLogger()

def init_flask_for_env():
  """
  Loads flask for lambda or local debug.
  """
  from os import environ
  if 'LOCAL_DEBUG' in environ:
    from flask import Flask
    return Flask(__name__)
  else:
    from flask_lambda import FlaskLambda
    return FlaskLambda(__name__)

def init_datastore():
  host = os.getenv('REDIS_HOST')
  port = os.getenv('REDIS_PORT')
  logging.info("Connecting to {host}:{port}".format(
    host=host,
    port=port
  ))

  ds = DataStore(host=host, port=int(port))
  return ds
    

app = init_flask_for_env()
ds = init_datastore()

@app.route('/heartbeat')
def hello_world():
  return 'Hello, World!'

@app.route("/init")
def init():
  with open('mappings.json') as file:
    mappings = loads(file.read())
    for key in mappings.keys():
      ds.set_symbol_translation(key, mappings[key])

@app.route('/s/<symbol>')
def resolve_symbol(symbol:str):
  return ds.resolve_symbol(symbol)
