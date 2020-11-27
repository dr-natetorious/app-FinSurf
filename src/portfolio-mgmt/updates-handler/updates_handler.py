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

def __unwrap_cwlogs_event(record:dict) -> dict:
  """
  CloudWatch to Kinesis sends as gzip(base64(text))
  """
  compressed = b64decode(record['kinesis']['data'])
  buf = BytesIO(compressed)
  with gzip.GzipFile(mode='rb', fileobj=buf) as file:
    with TextIOWrapper(file) as text_reader:
      return loads(text_reader.read())

def __get_messages_from_cwlog(cwlog_event:dict) -> List[dict]:
  # Change single to double quotes
  messages = [__hack_property_quotes(x['message']) for x in cwlog_event['logEvents']]
  
  # Convert from json to dict
  messages = [loads(m) for m in messages]
  return messages

def __hack_property_quotes(message:str)->str:
  return message.replace("'",'"')
