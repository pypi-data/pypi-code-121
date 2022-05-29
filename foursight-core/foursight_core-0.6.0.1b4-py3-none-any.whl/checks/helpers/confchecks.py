# Create a new confchecks.py for a new project (e.g. foursight-cgap)
from ...decorators import Decorators

# replace placeholder_prefix with an actual foursight_prefix 
deco = Decorators('placeholder_prefix')
CheckResult = deco.CheckResult
ActionResult = deco.ActionResult
check_function = deco.check_function
action_function = deco.action_function
