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

class UpdateAccountPositionHandler(AbstractRequestHandler):

  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('UpdateAccountPosition')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:

    update_type = handler_input.request_envelope.request.

    update_type = ask_utils.get_slot_value(handler_input,'update_type')
    symbol = ask_utils.get_slot_value(handler_input,'symbol')
    accountname = ask_utils.get_slot_value(handler_input,'accountname')    

    text = self.__process(update_type, symbol, accountname)
    return (
      handler_input.response_builder
      .speak(text)
      .response
    )
  
  def __process(self, update_type,symbol, accountname):
    return choice([
      'Sure, we can {} some {} in your {} account'.format(update_type,symbol,accountname),
    ])
