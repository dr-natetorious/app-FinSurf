import logging
from random import choice
from json import dumps, loads
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot
import ask_sdk_core.utils as ask_utils
from handlers.intents.BaseIntent import BaseIntent

class DescribeAccountPositionHandler(BaseIntent):

  def __init__(self):
    super().__init__()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DescribeAccountPosition')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    symbol = self.get_slot(handler_input,'symbol')
    accountname = self.get_slot(handler_input,'accountname')

    text = self.__process(symbol, accountname)
    return (
      handler_input.response_builder
      .speak(text)
      .set_should_end_session(False)
      .response
    )
  
  def __process(self, symbol, accountname):
    return choice([
      'I didnt find a {} position in your {} account'.format(symbol.internal_value, accountname.display_text),
      'Your net {} position in {} account is 10.2 shares with a notional value of $1250'.format(symbol.internal_value,accountname.display_text),
      'Your really short {} in {} account and should hedge the position'.format(symbol.internal_value, accountname.display_text),
    ])
