import logging
import os
import requests
from random import choice
from json import dumps, loads
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import ask_sdk_core.utils as ask_utils

class DescribeMarketConditionHandler(AbstractRequestHandler):

  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DescribeMarketCondition')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    date = ask_utils.get_slot_value(handler_input,'date')

    text = self.__process(date)
    return (
      handler_input.response_builder
      .speak(text)
      .response
    )
  
  def __process(self, date):
    return choice([
        "its a little choppy with low volume",
        "we're going to the moon today",
        "equities are approaching a local maximum, perhaps we should sell calls"
        "equities are oversold, i would consider selling puts here"])
