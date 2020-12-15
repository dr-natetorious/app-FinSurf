from typing import List
from base64 import b64decode
from json import loads,dumps
from io import BytesIO, TextIOWrapper
import gzip

class CloudWatchSubscriptionEventParser:

  def from_kinesis_event(self, kinesisEvent) -> List[dict]:
    results = []
    for record in kinesisEvent['Records']:
      cwlog_event = self.from_kinesis_record(record)
      for m in self.from_cwlog_event(cwlog_event):
        results.append(m)

    return results

  def from_kinesis_record(self,record:dict) -> dict:
    """
    CloudWatch to Kinesis sends as base64(gzip(utf8(text)))
    """
    compressed = b64decode(record['kinesis']['data'])
    buf = BytesIO(compressed)
    with gzip.GzipFile(mode='rb', fileobj=buf) as file:
      with TextIOWrapper(file) as text_reader:
        return loads(text_reader.read())

  def from_cwlog_event(self,cwlog_event:dict) -> List[dict]:
    # Change single to double quotes
    messages = [CloudWatchSubscriptionEventParser.__hack_property_quotes(x['message']) for x in cwlog_event['logEvents']]
    
    # Convert from json to dict
    messages = [loads(m) for m in messages]
    return messages

  @staticmethod
  def __hack_property_quotes(message:str)->str:
    return message.replace("'",'"')
