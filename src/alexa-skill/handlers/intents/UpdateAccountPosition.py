import logging
from random import choice
from json import dumps, loads
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot
import ask_sdk_core.utils as ask_utils
from handlers.intents.BaseIntent import BaseIntent

class UpdateAccountPositionHandler(BaseIntent):

  def __init__(self):
    super().__init__()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('UpdateAccountPosition')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    update_type = self.get_slot_value(handler_input,'update_type')
    symbol = self.get_slot_value(handler_input,'symbol')
    accountname = self.get_slot_value(handler_input,'accountname')

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
