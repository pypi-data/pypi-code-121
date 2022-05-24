from __future__ import annotations
from typing import BinaryIO, List, Optional, Tuple, Union

import re
import datetime
import operator

import ics
import PyPDF2

from .regex import ASSIGNMENT, EXPRESS, PERSON
from .utils import data2hash, flatten


class Sitzungsdienst:
    """
    Handles weekly PDF assignments as issued by 'web.sta'
    """

    def __init__(self, pdf_file: Optional[Union[BinaryIO, str]] = None) -> None:
        """
        Creates 'Sitzungsdienst' instance

        :param pdf_file: typing.BinaryIO|str Binary stream OR filepath representing PDF containing weekly assignments

        :return: None
        """

        # If provided ..
        if pdf_file:
            # .. load PDF file
            self.load_pdf(pdf_file)


    def load_pdf(self, pdf: Union[BinaryIO, str]) -> Sitzungsdienst:
        """
        Loads PDF contents for further processing

        :param pdf: typing.BinaryIO|str PDF file (either binary stream OR filepath)

        :return: sitzungsdienst.sta.Sitzungsdienst
        """

        # Create data array
        self.contents = {}

        # Fetch content from PDF file
        for i, page in enumerate(PyPDF2.PdfFileReader(pdf).pages):
            self.contents[i + 1] = [text.strip() for text in page.extractText().splitlines() if text]

        return self


    def extract_data(self) -> List[Dict[str, str]]:
        """
        Extracts weekly assignments from PDF contents, grouped by date

        :return: list<dict<str,str>> Weekly assignments
        :raises: Exception Missing PDF contents
        """

        # If PDF contents not present ..
        if not self.contents:
            # .. fail early
            raise Exception('Missing PDF contents!')

        # Create data array
        source = {}

        # Reset weekday buffer
        date = None

        # Extract assignment data
        for page_count, page in self.contents.items():
            # Reset mode
            is_live = False

            for index, text in enumerate(page):
                # Determine starting point ..
                if text == 'Anfahrt':
                    is_live = True

                    # .. and proceed with next entry
                    continue

                # Determine terminal point ..
                if text == 'Seite':
                    is_live = False

                    # .. and proceed with next entry
                    continue

                # Enforce entries between starting & terminal point
                if not is_live or 'Ende der Auflistung' in text:
                    continue

                # Determine current date / weekday
                if text in ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']:
                    date = page[index + 1]

                    if date not in source:
                        source[date] = []

                    # Proceed with next entry
                    continue

                # Proceed with next entry if it indicates ..
                # (1) .. current date
                if text == date:
                    continue

                # (2) .. follow-up appointment for main trial
                if text in ['F', '+']:
                    continue

                source[date].append(text)

        # Create data array
        unprocessed = []

        # Iterate over source data
        for date, raw in source.items():
            buffer = []
            court  = ''

            # Iterate over text blocks
            for index, text in enumerate(raw):
                if self.is_court(text):
                    court = text

                else:
                    buffer.append(text)

                if index + 1 == len(raw) or self.is_court(raw[index + 1]):
                    unprocessed.append({
                        'date': date,
                        'court': court,
                        'data': buffer,
                    })

                    # Reset buffer
                    buffer = []

        # Reset global data array
        data = []

        for item in unprocessed:
            events = []

            # Format data as string
            string = ' '.join(item['data'])

            # Find assignments
            matches = ASSIGNMENT.finditer(string)

            # If none found ..
            if not matches:
                # .. proceed to next entry
                continue

            for match in matches:
                data.append({
                    'date': self.format_date(item['date']),
                    'when': match.group('time'),
                    'who': self.format_people(match.group('assigned')),
                    'where': self.format_place(item['court'], match.group('where')),
                    'what': match.group('docket'),
                })

        # Sort data
        data.sort(key=operator.itemgetter('date', 'who', 'when', 'where', 'what'))

        return data


    def extract_express(self) -> List[Dict[str, str]]:
        """
        Extracts express service periods & assignees

        :return: list<dict<str,str>> Express service periods & assignees
        :raises: Exception Missing PDF contents
        """

        # If PDF contents not present ..
        if not self.contents:
            # .. fail early
            raise Exception('Missing PDF contents!')

        # Create data array
        express = []

        # Detect 'express mode'
        # (1) Activation
        is_express = False

        for index, text in enumerate(self.contents[1]):
            # Skip if no express service
            if text == 'Keine Einteilung':
                break

            # Determine express service ..
            if text == 'Eildienst':
                is_express = True

                # .. and proceed with next entry
                continue

            # Skip
            if text == 'Tag':
                break

            if is_express:
                express.append(text)

        # Combine data to string for easier regEx matching
        string = ' '.join(express)

        # Find matches
        matches = EXPRESS.finditer(string)

        # If none found ..
        if not matches:
            # .. return empty list
            return []

        # Create data buffer
        express = []

        # Loop over matched time periods & their assignees ..
        for match in matches:
            # .. storing their data
            express.append({
                'from': match.group('from'),
                'to': match.group('to'),
                'who': self.format_people(match.group('assigned')),
            })

        return express


    def extract_people(self, as_string: bool = True) -> List[str]:
        """
        Extracts assigned people from PDF contents

        :param as_string: bool Whether to export strings OR match objects

        :return: list<str> Assigned people
        """

        # If PDF contents not present ..
        if not self.contents:
            # .. fail early
            raise Exception('Missing PDF contents!')

        # Create data array
        people = set()

        # Determine whether texts contains people
        matches = PERSON.finditer(' '.join(flatten(self.contents.values())))

        # If they do ..
        if matches:
            # .. store people ..
            if as_string:
                # (1) .. as strings
                people.update([self.format_person(match) for match in matches])

            else:
                # (2) .. as match objects
                people.update([match for match in matches])

        return list(people)


    # UTILITIES

    def filter(self, query: Union[List[str], str], data: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, str]]:
        """
        Filters assignments by provided queries

        :param query: list<str>|str Search terms
        :param data: list<dict<str,str>> Assignments

        :return: list<dict<str,str>> Filtered assignments
        """

        # If no data provided ..
        if not data:
            # .. use fallback
            data = self.extract_data()

        # If query represents string ..
        if isinstance(query, str):
            # .. make it a list
            query = [query]

        # Create data buffer
        results = []

        # Loop over search terms in order to ..
        for term in query:
            # .. filter out relevant items
            results.extend([item for item in data if term.lower() in item['who'].lower()])

        return results


    def data2ics(self, data: Optional[List[Dict[str, str]]] = None, duration: int = 1) -> ics.Calendar:
        """
        Exports assignments as ICS calendar object

        :param data: list<dict<str,str>> Assignments
        :param duration: int Average duration of each assignment (in hours)

        :return: ics.Calendar
        :raises: Exception Missing assignment data
        """

        # If no data provided ..
        if not data:
            # .. use fallback
            data = self.extract_data()

        # Attempt to ..
        try:
            # .. import timezone library while ..
            import zoneinfo

        # .. adding fallback for Python < v3.9
        except ImportError:
            from backports import zoneinfo

        # Create calendar
        calendar = ics.Calendar(creator='S1SYPHOS')

        # Define timezone
        timezone = zoneinfo.ZoneInfo('Europe/Berlin')

        # Iterate over assignments
        for item in data:
            # Define timezone, date & times
            time = datetime.datetime.strptime(item['date'] + item['when'], '%Y-%m-%d%H:%M')
            begin = time.replace(tzinfo=timezone)
            end = begin + datetime.timedelta(hours=duration)

            # Create event
            event = ics.Event(
                uid = data2hash(item),
                name = 'Sitzungsdienst ({})'.format(item['what']),
                created = datetime.datetime.now(timezone),
                begin = begin,
                end = end,
                location = item['where']
            )

            # Add assignee(s) as attendee(s)
            for person in item['who'].split(';'):
                # Build attendee
                attendee = ics.Attendee('')

                # Edit name (= title, full name & department)
                attendee.common_name = person

                # Add to assignment
                event.add_attendee(attendee)

            # Add event to calendar
            calendar.events.add(event)

        return calendar


    # HELPERS

    def is_court(self, string: str) -> bool:
        """
        Checks whether string denotes district or regional court

        :param string: str String to be checked

        :return: bool Whether or not string denotes a court
        """

        if re.match(r'(?:AG|LG)\s', string.strip()):
            return True

        return False


    def format_date(self, string: str, separator: str = '-') -> str:
        """
        Formats given date using specified separator

        :param string: str String representing date
        :param separator: str Separator

        :return: str Formatted date
        """

        return separator.join(reversed(string.split('.')))


    def format_place(self, court: str, extra: str) -> str:
        """
        Formats court & additional information

        :param court: str String representing a court
        :param extra: str String holding additional information

        :return: str Formatted place
        """

        # Format string representing court
        string = court.replace(' ,', '').strip()

        return '{} {}'.format(string, extra.strip()) if extra else string


    def format_people(self, string: str) -> str:
        """
        Formats assigned people

        :param string: str String representing assigned people

        :return: str Formatted people
        """

        # Find matches
        matches = PERSON.finditer(string)

        # If none found ..
        if not matches:
            # .. return original string
            return string

        # Create data array
        people = []

        for match in matches:
            # Clean strings & combine them
            people.append(self.format_person(match))

        # Bring people together
        return '; '.join(people)


    def format_person(self, match: re.Match) -> str:
        """

        """

        return ' '.join([string.strip() for string in [
            match.group('title'),
            match.group('doc'),
            match.group('first'),
            match.group('last'),
            match.group('department'),
        ] if string])
