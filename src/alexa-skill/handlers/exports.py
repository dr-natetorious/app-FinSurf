from handlers.core.LaunchRequestHandler import LaunchRequestHandler
from handlers.intents.DescribeAccount import DescribeAccountHandler
from handlers.intents.DescribeAccountPosition import DescribeAccountPositionHandler
from handlers.intents.DescribeMarketCondition import DescribeMarketConditionHandler
from handlers.intents.UpdateAccountPosition import UpdateAccountPositionHandler
from handlers.intents.GetEarnings import GetEarningsByDateHandler
from handlers.intents.demo.StateBusinessProblem import StateBusinessProblemHandler
from handlers.intents.demo.HelpTradeStock import HelpTradeStockHandler

from handlers.core.errorhandlers import FallbackIntentHandler,CatchAllExceptionHandler

request_handlers = [
    # Default Actions
    LaunchRequestHandler(),
    
    # Demo Actions
    StateBusinessProblemHandler(),
    HelpTradeStockHandler(),

    # Describe object
    DescribeAccountHandler(),
    DescribeAccountPositionHandler(),
    DescribeMarketConditionHandler(),

    # Get remote object
    GetEarningsByDateHandler(),

    # Update object
    UpdateAccountPositionHandler(),

    # Unknown request
    FallbackIntentHandler(),
]