#!/usr/bin/env python3
"""Module for viewing events via the CLI"""

import argparse
from datetime import datetime, timedelta

from . import util

def load_events(search_name_for=""):
    """Load events, filter to reasonable time range, apply search"""
    events = util.load_events()
    events.sort(key=lambda x: x["date"])

    # Apply user search in event name
    events = [e for e in events if search_name_for in e["name"].lower()]
    events.sort(key=lambda x: x["date"] + x["start_time"])

    # Don't show dates that are unreasonably far, or before today
    years_from_now = (datetime.now() + timedelta(days=365*2)).strftime(util.DATE_FORMAT)
    today = datetime.now().strftime(util.DATE_FORMAT)
    events = [e for e in events if e["date"] < years_from_now]
    events = [e for e in events if e["date"] >= today]

    return events

def main():
    """Use CLI args to show relevant upcoming events"""
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("-a", action="store_true", help="print *a*ll events, not just 10")
    argument_parser.add_argument("-s", default="", help="*s*earch for this in event name")
    cli_args = argument_parser.parse_args()

    events = load_events(cli_args.s)

    if cli_args.a:
        util.print_oneline(events)
    else:
        util.print_oneline(events[:10])

if __name__ == "__main__":
    main()
