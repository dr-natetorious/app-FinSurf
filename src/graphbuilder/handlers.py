from typing import List
from json import loads,dumps
from CloudWatchSubscriptionEventParser import CloudWatchSubscriptionEventParser
from GraphWriter import GraphWriter
from base64 import b64decode

writer = GraphWriter()

def kinesis_event_handler(kinesisEvent, context):
  for record in kinesisEvent['Records']:
    
    # TODO: Collect.py L118 might be double wrapping
    data = record['kinesis']['data']
    decoded = b64decode(data).decode('utf-8')
    message = b64decode(decoded).decode('utf-8')
    message = loads(message)
    
    print('calling write_td_stream_message...')
    writer.write_td_stream_message(message)
    
