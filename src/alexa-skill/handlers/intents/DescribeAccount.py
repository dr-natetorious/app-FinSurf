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

class DescribeAccountHandler(AbstractRequestHandler):

  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DescribeAccount')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    accountname = ask_utils.get_slot_value(handler_input,'accountname')

    text = self.__process(accountname)
    return (
      handler_input.response_builder
      .speak(text)
      .response
    )
  
  def __process(self, accountname):
    return choice([
      'Your {} account is up 4% this quarter'.format(accountname),
      'In your {} account there are four upcoming earning announcements'.format(accountname),
      'A recent move in Tesla has impacted your {} account by $2500'.format(accountname),
    ])
