# Help messages
from grantme.constants.misc import PROG


PROG_HELP = (
    'This is a utility for "granting" exclusive/shared access to '
    "machines. It is purely advisory in the sense that neither permissions "
    "is necessarily required to access the host. Its purpose is to make you "
    "aware of the presence of other active users so that you don't disrupt "
    "their work.\n\n"
    "Use `{prog} --mode {{exclusive,shared}} --duration 2h30m to obtain/prolong"
    "permission for 2 hours and 30 minutes.\n"
    "Use `{prog} --revoke` to invalidate your granted permission.\n"
    "Use `{prog} --revoke --user USER` to invalidate other users' granted"
    "permission.\n"
    "Use `{prog} --status` to view permissions of yours and other users'.".format(
        prog=PROG
    )
)
DURATION_HELP = (
    'Expected access duration, formatted as "?w?d?h?m?s". Default to "30m". You can'
    " rerun {prog} to prolong permission.".format(prog=PROG)
)
USER_HELP = (
    "The user whose permissions should be revoked. Defaults to the current login user."
)
INIT_HELP = (
    "Initialize the backend database. Root privilege might be needed (i.e., `sudo`)."
)

# Info
SLOCK_CMD = "{prog} --mode shared --duration ?d?h?m?s".format(prog=PROG)
XLOCK_CMD = "{prog} --mode exclusive --duration ?d?h?m?s".format(prog=PROG)
PROLONG_OK = "Permission is successfully prolonged."
UPGRADE_OK = "Shared permission upgraded to an exclusive permission."

# Warnings
DO_NOT_DISTURB = "Please **AVOID DEMANDING TASKS**, so as to not disrupt others."
NOTHING_REVOKED = "No permission is currently granted; nothing is revoked."
ATTEMPT_SLOCK_WITH_XLOCK = (
    "An exclusive permission already exists. Ignoring `--mode shared`."
)
ATTEMPT_SHORTER_DURATION_THAN_ALREADY_GRANTED = (
    "A permission that expires later than the given duration already exists."
    "No change is made."
)
