import logging
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

from LaunchRequestHandler import LaunchRequestHandler
from FetchEarningsByDate import FetchEarningsByDateHandler
from errorhandlers import FallbackIntentHandler, CatchAllExceptionHandler
from interceptors import LoggingRequestInterceptor, LoggingResponseInterceptor

sb = CustomSkillBuilder(api_client=DefaultApiClient())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(FetchEarningsByDateHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_response_interceptor(LoggingResponseInterceptor())
sb.add_global_request_interceptor(LoggingRequestInterceptor())

# This is the exported entry point.
lambda_handler = sb.lambda_handler()
