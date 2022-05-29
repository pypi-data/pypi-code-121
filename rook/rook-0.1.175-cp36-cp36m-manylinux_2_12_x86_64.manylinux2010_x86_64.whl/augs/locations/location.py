from rook.logger import logger
from rook.user_warnings import UserWarnings
from rook.processor.error import Error


class Location(object):
    def __init__(self, output, aug):
        self._output = output
        self._aug = aug
        self._enabled = True

        self._status = None
        self._warningCache = {}
        self._logCache = {}

    @property
    def aug_id(self):
        return self._aug.aug_id

    def add_aug(self, trigger_services):
        """Use the location to add the Aug to the relevant trigger service."""
        try:
            self._add_aug_internal(trigger_services)
        except Exception as exc:
            message = "Exception when adding aug"
            logger.exception(message + " " + self.aug_id + " : " + str(exc))
            self.set_error(Error(exc=exc, message=message))

    def _add_aug_internal(self, trigger_services):
        raise NotImplementedError()

    def execute(self, frame, extracted):
        if not self._enabled:
            return

        with UserWarnings(self):
            try:
                self._aug.execute(frame, extracted, self._output)
            # Don't stop test exceptions from propagating
            except AssertionError:
                raise
            # Catch and silence everything else
            except Exception as exc:
                message = "Exception while processing Aug"
                rook_error = Error(exc=exc, message=message)

                if not self._should_silence_log(rook_error, self._logCache):
                    logger.exception(message)

                self.send_warning(rook_error)

    def set_active(self):
        self._send_rule_status("Active")

    def set_pending(self):
        self._send_rule_status("Pending")

    def set_removed(self):
        self._send_rule_status("Deleted")

    def set_error(self, error):
        self._send_rule_status("Error", error)

    def set_unknown(self, error):
        self._send_rule_status("Unknown", error)

    def send_warning(self, error):
        if self._should_silence_log(error, self._warningCache):
            return

        logger.warning(error.message)

        self._output.send_warning(self.aug_id, error)

    def _send_rule_status(self, status, error=None):
        if self._status == status:
            return

        logger.info("Updating rule status for %s to %s", self.aug_id, status)

        self._status = status
        self._output.send_rule_status(self.aug_id, status, error)

    def _should_silence_log(self, error, log_cache):
        if error.message in log_cache or len(log_cache) >= 10:
            return True

        log_cache[error.message] = True

        return False