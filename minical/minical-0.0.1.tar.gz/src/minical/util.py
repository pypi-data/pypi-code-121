"""
Utility functions
"""
import copy
from datetime import datetime, timedelta
import os
import re

from .errors import BadEventError

EVENTS_DIR = os.environ.get("MINICAL_EVENTS_DIR", "events")
DATE_FORMAT = "%Y-%m-%d"

if not os.path.isdir(EVENTS_DIR):
    os.mkdir(EVENTS_DIR)

def parse_event_text(event_text):
    """Take key/val pairs from file and turn into a dict"""

    # re.split would normaly exclude the matching part, but subgroups will be kept
    # So this just finds the keys and the stuff after them
    keys_vals = re.split(r"^\s*(\w{3,}):", event_text, flags=re.MULTILINE)
    if keys_vals[0] == "":
        # You have nothing to the left of the first match, so discard that.
        keys_vals.pop(0)
    as_pairs = [(keys_vals[i], keys_vals[i+1]) for i in range(len(keys_vals)) if i % 2 == 0]

    event = dict(as_pairs)
    for key in event:
        event[key] = event[key].strip()
    return event

def load_event_from_file(event_name_or_path, is_path=False):
    """load event text and parse it"""

    basename = os.path.basename(event_name_or_path)
    assert re.match(r"^\w+$", basename)

    # Normally, just want to pass a basename, but you could pass a full path too.
    if not is_path:
        with open(os.path.join(EVENTS_DIR, basename), encoding="utf8") as f_in:
            event_text = f_in.read()
    else:
        with open(event_name_or_path, encoding="utf8") as f_in:
            event_text = f_in.read()

    event = parse_event_text(event_text)

    add_extra_date_info(event)
    event["notes"] = event["notes"].replace("NEWLINE", "\n")
    event["orig_text"] = event_text
    return event


def add_extra_date_info(event):
    """add extra data info like dow, days until"""
    date_obj = datetime.strptime(event["date"], DATE_FORMAT)
    event["day_of_week"] = date_obj.strftime("%a")
    event["days_until"] = round((date_obj - datetime.today()).total_seconds() / 86400, 1)


def load_events(expand=True):
    """Load events, possibly creating 'fake' events that are the result of recurring events"""
    orig_events = []
    for event_name in os.listdir(EVENTS_DIR):
        if not event_name.startswith("."):
            orig_events.append(load_event_from_file(event_name))

    additional_events = []
    if expand:
        for event in orig_events:
            additional_events += expand_event(event)

    return orig_events + additional_events


def print_oneline(events):
    """Print a concise representation of the event"""
    for e in events:
        print(
            "%s (%s), %s, %s (in %d days)" % (
                e["date"], e["day_of_week"], e["start_time"], e["name"], e["days_until"]))


def expand_event(event):
    """Apply recurring info to get copies of the event on other days"""
    if not event.get("recurs"):
        return []

    additional_events = []
    recurs = event["recurs"]
    start_date = datetime.strptime(event["date"], DATE_FORMAT)
    stop_date = datetime.strptime(event["recurs_until"], DATE_FORMAT)

    date_step = start_date
    while date_step < stop_date:
        date_step += timedelta(days=1)
        date_match = False
        if recurs == "annually":
            if date_step.month == start_date.month and date_step.day == start_date.day:
                date_match = True
        elif recurs == "monthly":
            if date_step.day == start_date.day:
                date_match = True
        elif recurs == "weekly":
            if date_step.weekday() == start_date.weekday():
                date_match = True

        if date_match:
            event_copy = copy.deepcopy(event)
            event_copy["date"] = date_step.strftime(DATE_FORMAT)
            add_extra_date_info(event_copy)

            if event_copy["date"] not in event.get("skip_dates", ""):
                additional_events.append(event_copy)

    return additional_events

def validate_event(event):
    """Raise errors if event is bad"""
    # pylint: disable=too-many-branches
    name_regex = r"^\w+$"
    if not re.match(name_regex, event["name"]):
        raise BadEventError(f"Name should follow regex {name_regex}")

    try:
        datetime.strptime(event["date"], "%Y-%m-%d")
    except ValueError as e:
        raise BadEventError("Couldn't parse the date, should be YYYY-mm-dd") from e

    if not re.match(r"^\d\d:\d\d$", event["start_time"]):
        raise BadEventError("Bad start time")
    if not event["duration_minutes"].isdigit():
        raise BadEventError("Bad duration")

    if event["recurs"]:
        if event["recurs"].lower() not in ("", "weekly", "monthly", "annually"):
            raise BadEventError("Value for 'recurs' should be blank, weekly, monthly, or annually")

    if event["recurs_until"]:
        if not event["recurs"]:
            raise BadEventError("'recurs' must be set if 'recurs_until' is")
        try:
            datetime.strptime(event["recurs_until"], "%Y-%m-%d")
        except ValueError as e:
            raise BadEventError("Couldn't parse the recurs_until date, should be YYYY-mm-dd") from e

    if event.get("skip_dates"):
        if not event["recurs"]:
            raise BadEventError("'recurs' must be set if 'skip_dates' is")
        skip_dates = event["skip_dates"].split(",")
        skip_dates = [d.strip() for d in skip_dates if d.strip()]
        for date in skip_dates:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError as e:
                raise BadEventError(f"Bad skip date '{date}', should be YYYY-mm-dd") from e

if __name__ == "__main__":
    pass
