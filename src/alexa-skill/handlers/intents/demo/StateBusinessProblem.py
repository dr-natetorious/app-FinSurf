import logging
from random import choice
from json import dumps, loads
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot
import ask_sdk_core.utils as ask_utils
from handlers.intents.BaseIntent import BaseIntent
from aws_xray_sdk.core import xray_recorder

class StateBusinessProblemHandler(BaseIntent):

  def __init__(self):
    super().__init__()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DemoStateBusinessProblem')(handler_input)

  @xray_recorder.capture('handle')
  def handle(self, handler_input:HandlerInput) -> Response:
    text = """
      <speak>
        <p>
          <amazon:domain name="conversational">
            <audio src="soundbank://soundlibrary/telephones/car_cell_phones/car_cell_phones_02"/>
            <voice name="Matthew">Hello, this is Mathew.</voice>
            <voice name="Salli">Hey Matt, this is Salli from Octank Financial. Do you have a moment to talk?</voice>
            <voice name="Matthew">Sure</voice>
            <voice name="Salli">Did you know Telsa gained over 700% last year, and the tech market doubled?</voice>
            <voice name="Matthew">Ah yes, that was painful to watch while all of my money sat in a savings account.</voice>
            <voice name="Salli">Any reason you didn't invest?</voice>
            <voice name="Matthew">Oh, I don't understand how any of that works. Trading apps are just too confusing, so I play it safe.</voice>
            <voice name="Salli">That's exactly why I'm calling today.  Octank has a new Alexa skill that makes it easy for anyone to get started</voice>
            <audio src="soundbank://soundlibrary/cloth_leather_paper/money_coins/money_coins_05"/>
            <voice name="Matthew">Easy you say?  We'll that's a welcomed change! Tell me more!</voice>
          </amazon:domain>
        </p>
      </speak>
    """
    return (
      handler_input.response_builder
      .set_should_end_session(False)
      .speak(text)
      .response
    )
