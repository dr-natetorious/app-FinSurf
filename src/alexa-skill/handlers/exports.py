from handlers.core.LaunchRequestHandler import LaunchRequestHandler
from handlers.finsurf.FetchEarnings import FetchEarningsByDateHandler
from handlers.finsurf.DescribeMarketCondition import DescribeMarketConditionHandler
from handlers.core.errorhandlers import FallbackIntentHandler,CatchAllExceptionHandler

request_handlers = [
    LaunchRequestHandler(),
    FetchEarningsByDateHandler(),
    DescribeMarketConditionHandler(),
    FallbackIntentHandler(),
    CatchAllExceptionHandler()
]