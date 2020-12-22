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

class BaseIntent(AbstractRequestHandler):

  def __init__(self):
    super().__init__()
    self.logger = logging.getLogger()

  def get_slot_value(self, handler_input:HandlerInput, name:str)->str:
    slot = ask_utils.get_slot(handler_input,name)

    self.logger.debug('inspecting slot={} with struct={}'.format(slot.name, slot.to_dict()))
    if slot.resolutions != None and slot.resolutions.resolutions_per_authority != None:
      self.logger.debug('slot {} has resolutions..'.format(slot.name))
      for match in slot.resolutions.resolutions_per_authority:
        self.logger.debug('checking match.status={}'.format(match.status))
        if match.status.code == StatusCode.ER_SUCCESS_MATCH:
          self.logger.debug('valid option returning {}'.format(match.to_dict()))
          return match.values[0].value.id
    
    self.logger.warn('slot {} is missing valid resolution defaulting to {}'.format(name,slot.value))
    return slot.value