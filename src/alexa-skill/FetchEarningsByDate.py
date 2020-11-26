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

class FetchEarningsByDateHandler(AbstractRequestHandler):

  def __init__(self):
    self.logger = logging.getLogger()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('FetchEarningsByDate')(handler_input)

  def handle(self, handler_input:HandlerInput) -> Response:
    self.logger.info(dumps(handler_input))

    return (
      handler_input.response_builder
      .speak('let me check on that')
      .response
    )
  