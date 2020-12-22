import logging
from random import choice
from json import dumps, loads
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot
import ask_sdk_core.utils as ask_utils
from handlers.intents.BaseIntent import BaseIntent

class DescribeAccountHandler(BaseIntent):

  def __init__(self):
    super().__init__()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DescribeAccount')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    accountname = self.get_slot_value(handler_input,'accountname')

    text = self.__process(accountname)
    return (
      handler_input.response_builder
      .set_should_end_session(False)
      .speak(text)
      .response
    )
  
  def __process(self, accountname):
    return choice([
      'Your {} account is up 4% this quarter'.format(accountname),
      'In your {} account there are four upcoming earning announcements'.format(accountname),
      'A recent move in Tesla has impacted your {} account by $2500'.format(accountname),
    ])
