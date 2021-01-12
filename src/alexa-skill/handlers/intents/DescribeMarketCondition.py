import logging
from random import choice
from json import dumps, loads
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot
import ask_sdk_core.utils as ask_utils
from handlers.intents.BaseIntent import BaseIntent

class DescribeMarketConditionHandler(BaseIntent):

  def __init__(self):
    super().__init__()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DescribeMarketCondition')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    text = self.__process()
    return (
      handler_input.response_builder
      .speak(text)
      .set_should_end_session(False)
      .response
    )
  
  def __process(self):
    return choice([
      "its a little choppy with low volume",
      "we're going to the moon today",
      "equities are approaching a local maximum, perhaps we should sell calls",
      "equities are oversold, i would consider selling puts here"])
