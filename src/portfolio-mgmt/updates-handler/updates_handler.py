from typing import List
from base64 import b64decode
from json import loads,dumps
from io import BytesIO, TextIOWrapper
from cwlogutil import CloudWatchSubscriptionEventParser
import gzip

parser = CloudWatchSubscriptionEventParser()

def lambda_handler(kinesisEvent,context):
  messages = parser.from_kinesis_event(kinesisEvent)
  print(dumps(messages))
