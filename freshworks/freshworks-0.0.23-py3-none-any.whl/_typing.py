from typing import Dict


# The time after which an escalation email is sent if a ticket remains
# unassigned. The accepted values are
# * "30m" for 30 minutes
# * "1h" for 1 hour
# * "2h" for 2 hours
# * "4h" for 4 hours
# * "8h" for 8 hours
# * "12h" for 12 hours
# * "1d" for 1 day
# * "2d" for 2 days
# * "3d" for 3 days
TimeDeltaString = str  # Type Alias

TicketJSON = Dict  # Type Alias
