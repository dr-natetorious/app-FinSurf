from typing import List
from json import loads,dumps
from CloudWatchSubscriptionEventParser import CloudWatchSubscriptionEventParser
from GraphWriter import GraphWriter

parser = CloudWatchSubscriptionEventParser()
writer = GraphWriter()
def subscription_handler(kinesisEvent,context):
  messages = parser.from_kinesis_event(kinesisEvent)
  for message in messages:
    writer.write_td_stream_message(message)

def kinesis_event_handler(kinesisEvent, context):
  for record in kinesisEvent['Records']:
    print(record['kinesis']['data'])
