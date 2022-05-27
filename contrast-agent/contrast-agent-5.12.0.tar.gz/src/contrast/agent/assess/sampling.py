# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.

from contrast.agent.settings import Settings
from contrast.utils.decorators import fail_quietly
from contrast.utils.timer import now_ms

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

# Safe to look for settings at module level because sampling feature
# should always run during an agent-backed request.
settings = Settings()

REQUESTS = dict()
LOGGED_SAMPLING_MESSAGE = False


def enabled():
    global LOGGED_SAMPLING_MESSAGE
    enabled = settings.is_assess_enabled() and settings.config.get(
        "assess.sampling.enable"
    )

    if not LOGGED_SAMPLING_MESSAGE and enabled:
        logger.info(
            "Contrast assess.sampling is enabled in your configuration. "
            "Not all requests will be analyzed."
        )
        LOGGED_SAMPLING_MESSAGE = True

    return enabled


# If we can't determine sampling, it's better to analyze the request.
@fail_quietly("Unable to determine sampling", False)
def meets_criteria(context) -> bool:
    """
    If a request meets criteria for sampling, agent should not analyze request.

    Criteria is met if request happens inside a sampling time window and request
    count minus baseline doesn't meet frequency setting.
    """
    if context.hash is None:
        # If we cannot determine the uniqueness of this request, it's better
        # to analyze the request
        return False

    if context.hash in REQUESTS:
        history = REQUESTS[context.hash]
    else:
        history = REQUESTS[context.hash] = RequestHistory()

    history.hit()

    # if sampling window has been exceeded, reset it.
    if history.elapsed() >= settings.config.get("assess.sampling.window_ms"):
        history.reset()
        return False

    # once hits exceed baseline setting, limit analysis based on frequency setting.
    baseline = settings.config.get("assess.sampling.baseline")
    frequency = settings.config.get("assess.sampling.request_frequency")

    return not (history.hits <= baseline or (history.hits - baseline) % frequency == 0)


class RequestHistory(object):
    def __init__(self):
        self._start = now_ms()
        self._hit = 0

    @property
    def hits(self):
        return self._hit

    def elapsed(self):
        return now_ms() - self._start

    def hit(self):
        """Increment attempted requests, not analyzed requests"""
        self._hit += 1

    def reset(self):
        self._start = now_ms()
        self._hit = 1

    def __repr__(self):
        return f"Started at: {self._start} - Hit : {self._hit}"
