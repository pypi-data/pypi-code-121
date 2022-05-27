"""
Constants for easy_time_tracker
"""
import os
from pathlib import Path

# The absolute path to the easy-time-tracker directory
EASY_TIME_TRACKER_BASE_PATH = os.path.split(os.path.split(os.path.abspath(__file__))[0])[0]
# The name to use for the current record
EASY_TIME_TRACKER_CURRENT_RECORD = os.getenv('EASY_TIME_TRACKER_CURRENT_RECORD') or \
                                   os.path.join(Path.home(), 'easy-time-tracker-data', 'current_record.json')
# The name to use for the completed records
EASY_TIME_TRACKER_COMPLETED_RECORDS = os.getenv('EASY_TIME_TRACKER_COMPLETED_RECORDS') or \
                                      os.path.join(Path.home(), 'easy-time-tracker-data', 'completed_records.json')
