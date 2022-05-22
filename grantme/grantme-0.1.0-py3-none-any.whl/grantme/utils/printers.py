from grantme.constants.msgs import SLOCK_CMD, XLOCK_CMD


# Formatting codes
# copied from https://stackoverflow.com/a/287944
class FormatCode:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    ENDC = "\033[0m"


def show_sep_line():
    print(FormatCode.HEADER, "#" * 80, FormatCode.ENDC, sep="")


def slock_guide():
    print("You can obtain shared access with")
    print("\t" + SLOCK_CMD)


def xlock_guide():
    print("You can obtain exclusive access with")
    print("\t" + XLOCK_CMD)


def show_no_lock():
    print("Neither exclusive nor shared access is not granted yet.")
    slock_guide()
    xlock_guide()


def show_expire(expire, whose=None):
    if whose is None:
        subject = "The permission"
    else:
        subject = "{whose} permission".format(whose=whose)
    print(
        "{subject} expires at ".format(subject=subject)
        + FormatCode.BOLD
        + str(expire)
        + FormatCode.ENDC
        + "."
    )


def show_granted(mode, expire, highlighted_user=None, others=[]):
    print(mode, "access is granted to")
    if highlighted_user is None:
        who = ", ".join(others)
    else:
        who = FormatCode.BOLD + highlighted_user + FormatCode.ENDC
        if len(others) > 0:
            who += ", "
            who += ", ".join(others)
    print("\t" + who + ",")
    print(
        "(the last of) which expires at "
        + FormatCode.BOLD
        + str(expire)
        + FormatCode.ENDC
        + "."
    )


def show_grant_ok(mode, who):
    ok("{who}'s {mode} permission is successfully granted.".format(who=who, mode=mode))


def show_revoke_ok(mode, who):
    ok("{who}'s {mode} permission is successfully revoked.".format(who=who, mode=mode))


def ok(msg):
    print(FormatCode.OKGREEN + msg + FormatCode.ENDC)


def info(msg):
    print(FormatCode.OKBLUE + msg + FormatCode.ENDC)


def warning(msg):
    print(FormatCode.WARNING + msg + FormatCode.ENDC)


# When some op fails within expectation
def failure(msg):
    print(FormatCode.FAIL + msg + FormatCode.ENDC)


# Unexpected errors
def error(msg):
    print(FormatCode.FAIL + msg + FormatCode.ENDC)
