import logging
from random import choice
from json import dumps, loads
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Intent,Response, IntentConfirmationStatus, Slot
import ask_sdk_core.utils as ask_utils
from handlers.intents.BaseIntent import BaseIntent
from aws_xray_sdk.core import xray_recorder

class HelpTradeStockHandler(BaseIntent):

  def __init__(self):
    super().__init__()

  def can_handle(self, handler_input:HandlerInput) -> bool:
    return ask_utils.is_intent_name('DemoHelpTradeStock')(handler_input)

  @xray_recorder.capture('handle')
  def handle(self, handler_input:HandlerInput) -> Response:
    strategy = self.get_slot(handler_input, 'strategy')
    symbol = self.get_slot(handler_input, 'symbol')
    
    text = 'Building response for {} with {} security'.format(strategy,symbol)

    if strategy.internal_value == 'SELL':
      text = """
        <speak>
          <p>
            <amazon:domain name="conversational">
              <voice name="Salli">Just a heads up... {symbol} is being panic sold due to a news event.</voice>
              <voice name="Matthew"><break time="200ms"/>Tell me more</voice>
              <voice name="Salli">According to WSJ was a major service outage, but this event is unlikely to change any fundamentals.  Would you like to know more?</voice>
              <voice name="Matthew"><break time="200ms"/>No, <break time="200ms"/>what is the best trade in {symbol} for my account?</voice>
              <voice name="Salli">You would have a 74% chance of making $0.75 within 15 days using a skewed iron condor.  This trade comes with a max loss of $3.50.</voice>
              <voice name="Matthew">Those are pretty good odds, let's do two of those</voice>
              <voice name="Salli">
                Confirmed and sending...<break time="200ms"/>.  Filled <audio src="soundbank://soundlibrary/human/amzn_sfx_crowd_excited_cheer_01"/>
              </voice>
            </amazon:domain>
          </p>
        </speak>
      """
    elif strategy.internal_value == 'BUY':
      text = """
        <speak>
          <p>
            <amazon:domain name="conversational">
              <voice name="Salli">It looks like {symbol} is at an all time high.  Would you like me to search for a less risky entry point?</voice>
              <voice name="Matthew">Yes.</voice>
              <voice name="Salli">Are you willing to hold shares in {symbol}?</voice>
              <voice name="Matthew">Yes.</voice>
              <voice name="Salli">How about we target buying the shares 4% lower within 32 days?  While waiting you'll collect $23.52 in daily interest.</voice>
              <voice name="Matthew"><break time="200ms"/>Explain how that works</voice>
              <voice name="Salli">Essentially you are selling a short term insurance product, called a bullish put spread, for roughly $723.12.</voice>
              <voice name="Matthew"><break time="200ms"/>What if the stock continues going up?</voice>
              <voice name="Salli">Then the insurance expires worthless and you keep all of the premium payments.</voice>
              <voice name="Matthew"><break time="200ms"/>What if the stock crashes?</voice>
              <voice name="Salli">If the stock crashes then you might need to buy 100 shares for $652.50 less the insurance payments recieved.</voice>
              <voice name="Matthew"><break time="200ms"/>That sounds like a better deal.  <amazon:emotion name="excited">Let's do that!</amazon:emotion></voice>
              <voice name="Salli">
                Confirmed and sending...<break time="200ms"/>.  Filled <audio src="soundbank://soundlibrary/human/amzn_sfx_crowd_excited_cheer_01"/>
              </voice>
            </amazon:domain>
          </p>
        </speak>
      """
    return (
      handler_input.response_builder
      .set_should_end_session(False)
      .speak(text.format(strategy=strategy.display_text,symbol=symbol.display_text))
      .response
    )
