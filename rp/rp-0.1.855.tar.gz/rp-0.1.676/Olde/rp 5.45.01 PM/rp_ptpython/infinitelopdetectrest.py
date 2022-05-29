def timeout(f,t):
    import signal

    class TimeoutException(Exception):   # Custom exception class
        pass

    def timeout_handler(signum, frame):   # Custom signal handler
        raise TimeoutException

    # Change the behavior of SIGALRM
    signal.signal(signal.SIGALRM, timeout_handler)
    # https://stackoverflow.com/questions/25027122/break-the-function-after-certain-time
    # Start the timer. Once 5 seconds are over, a SIGALRM signal is sent.
    signal.alarm(t)
    # This try/except loop ensures that
    #   you'll catch TimeoutException when it's sent.
    try:
        f()
    except TimeoutException:
        return # continue the for loop if function A takes more than 5 second
def inf():
    while True:pass
timeout(inf,3)