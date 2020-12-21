import logging
import os
import requests
from random import choice
from json import dumps, loads
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot
from ask_sdk_model.slu.entityresolution import Resolutions, Resolution, ValueWrapper, Value,Status,StatusCode
from ask_sdk_model.dialog import ElicitSlotDirective
import ask_sdk_core.utils as ask_utils

class DescribeAccountPositionHandler(AbstractRequestHandler):

  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DescribeAccountPosition')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    symbol = ask_utils.get_slot_value(handler_input,'symbol')
    accountname = ask_utils.get_slot_value(handler_input,'accountname')

    text = self.__process(symbol, accountname)
    return (
      handler_input.response_builder
      .speak(text)
      .response
    )
  
  def __process(self, symbol, accountname):
    return choice([
      'I didnt find a {} position in your {} account'.format(symbol, accountname),
      'Your net {} position in {} account is 10.2 shares with a notional value of $1250'.format(symbol,accountname),
      'Your really short {} in {} account and should hedge the position'.format(symbol, accountname),
    ])
