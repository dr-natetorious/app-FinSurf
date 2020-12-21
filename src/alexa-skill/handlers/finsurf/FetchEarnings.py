import logging
import os
import requests
from json import dumps, loads
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.dispatch_components import AbstractResponseInterceptor
from ask_sdk_core.dispatch_components import AbstractRequestInterceptor
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_core.exceptions import AskSdkException
import ask_sdk_core.utils as ask_utils

from clients.FriendlyNamedClient import FriendlyNamedClient
fnapi = FriendlyNamedClient()

class FetchEarningsByDateHandler(AbstractRequestHandler):

  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('FetchEarningsByDate')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    date = ask_utils.get_slot_value(handler_input,'date')

    text = self.__process(date)
    return (
      handler_input.response_builder
      .speak(text)
      .response
    )
  
  def __process(self, date):
    resource_url = os.environ['EARNINGS_API']
    if resource_url.endswith('/') == False:
      resource_url+='/'
    resource_url += date

    df = loads(requests.get(resource_url).text)

    return "There are {count} reportings including {highlights}".format(
      count=len(df),
      highlights=", ".join([fnapi.resolve_symbol(x['symbol']) for x in df][0:3])
    )
