import logging
import os
import requests
from random import choice
from json import dumps, loads
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot, IntentRequest
from ask_sdk_model.slu.entityresolution import Resolutions, Resolution, ValueWrapper, Value,Status,StatusCode
from ask_sdk_model.dialog import ElicitSlotDirective
import ask_sdk_core.utils as ask_utils

class SlotWrapper:
  """
  Represents a wrapper to the Slot object
  """
  def __init__(self, slot:Slot)->None:
    if slot == None:
      raise ValueError('No slot was provided.')
    
    self.slot = slot

  @property
  def internal_value(self) -> str:
    if self.slot.resolutions != None and self.slot.resolutions.resolutions_per_authority != None:
      for match in self.slot.resolutions.resolutions_per_authority:
        if match.status.code == StatusCode.ER_SUCCESS_MATCH:
          return match.values[0].value.id

    return self.slot.value

  @property
  def display_text(self) -> str:
    return self.slot.value

class BaseIntent(AbstractRequestHandler):

  def __init__(self):
    super().__init__()
    self.logger = logging.getLogger()
  
  def get_slot(self, handler_input:HandlerInput, name:str)->SlotWrapper:
    slot = ask_utils.get_slot(handler_input,name)
    return SlotWrapper(slot)
  