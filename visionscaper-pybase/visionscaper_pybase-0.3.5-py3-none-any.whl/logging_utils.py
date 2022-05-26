import traceback

def log_exception(logger, message, e):
    logger.error('An exception occurred : %s' % str(message))  # the exception instance
    logger.error('Exception type : %s' % type(e))  # the exception instance
    logger.error(e)  # the exception instance
    traceback.print_exc()
