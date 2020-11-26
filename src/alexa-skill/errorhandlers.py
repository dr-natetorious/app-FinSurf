import logging
from json import dumps
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

class FallbackIntentHandler(AbstractRequestHandler):

  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('AMAZON.FallbackIntent')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    return (
      handler_input.response_builder
      .speak('oh no! crash.')
      .response
    )
  
class CatchAllExceptionHandler(AbstractExceptionHandler):
  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput, exception:Exception) -> bool:
    return True

  def handle(self, handler_input:HandlerInput, exception:Exception) -> Response:
    self.logger.error(exception, exc_info=True)
    self.logger.info(dumps(handler_input))

    return (
      handler_input.response_builder
      .speak('oh no! crash.')
      .response
    )