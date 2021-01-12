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
              <voice name="Matthew">Hey Fin Surf, should I sell my {symbol} shares</voice>
              <voice name="Salli">Just a heads up... {symbol} is being panic sold due to a news event.</voice>
              <voice name="Matthew"><break time="200ms"/>Tell me more</voice>
              <voice name="Salli"><break time="200ms"/>According to WSJ there was a major service outage, but this event is unlikely to change any fundamentals.  Would you like to know more?</voice>
              <voice name="Matthew"><break time="200ms"/>No, <break time="200ms"/>what is the best trade in {symbol} for my account?</voice>
              <voice name="Salli"><break time="200ms"/>You would have a 74% chance of making $0.75 within 15 days using a skewed iron condor.  This trade comes with a max loss of $3.50.</voice>
              <voice name="Matthew"><break time="200ms"/>Those are pretty good odds, let's do two of those</voice>
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
              <voice name="Justin">Hey Fin Surf, should I buy shares in {symbol}?</voice>
              <voice name="Salli">
                <amazon:domain name="long-form">
                  Did you know that your various ETFs and Mutal Funds already contain {symbol}?
                  Across these positions you have a notional equivalent of $12,532.17 exposure.
                  Are you still interested in purchasing additional shares? 
                </amazon:domain>
              </voice>
              <voice name="Justin"><break time="200ms"/>Yes.</voice>
              <voice name="Salli"><break time="300ms"/>It looks like {symbol} is at an all time high.  Would you like me to search for a less risky entry point?</voice>
              <voice name="Justin"><break time="200ms"/>Sure.</voice>
              <voice name="Salli"><break time="300ms"/>Are you willing to hold shares in {symbol}?</voice>
              <voice name="Justin"><break time="300ms"/>Alright.</voice>
              <voice name="Salli">I can place an Octank Smart Limit Order at 4% lower for 32 days?  While waiting you'll collect $23.52 in daily interest.</voice>
              <voice name="Justin"><break time="350ms"/>Explain how that works</voice>
              <voice name="Salli"><break time="200ms"/>
                <amazon:domain name="long-form">
                  Essentially you are selling a short term insurance product, called a bullish put spread, for $723.12.
                  During the 32 day period the insurance product decays producing interest-like payments in your favor.
                  If the stock continues rising, then the insurance becomes worthless and you keep the $732.
                  However, if {symbol} falls more than 4%, then you might need to purchase the shares at a breakeven point of $648.38 each.
                </amazon:domain>
              </voice>
              <voice name="Justin"><break time="300ms"/>That sounds like a better deal.  <amazon:emotion name="excited">Let's do that!</amazon:emotion></voice>
              <voice name="Salli">
                Confirmed and sending...<break time="200ms"/>.  Filled <audio src="soundbank://soundlibrary/human/amzn_sfx_crowd_excited_cheer_01"/>
              </voice>
            </amazon:domain>
          </p>
        </speak>
      """
    return (
      handler_input.response_builder
      .set_should_end_session(True)
      .speak(text.format(strategy=strategy.display_text,symbol=symbol.display_text))
      .response
    )
