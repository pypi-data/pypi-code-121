#!/usr/bin/python3

"""
format concerts data into final output and write it to disk
"""

import os
import json

from datetime import datetime

import feedgenerator as fg


def pretty_strings(concert):
    """Extract relevant data from concert dict and format it"""
    event_id = concert['id']
    artists = ", ".join(map(str, concert['lineup']))
    date = datetime.fromisoformat(concert['datetime']).strftime("%Y-%m-%d %H:%M")
    venue = concert['venue']['name'] + ", " + concert['venue']['city']
    description = concert['description']
    url = 'https://www.bandsintown.com/e/' + event_id
    return event_id, artists, date, venue, description, url


def atom(concert_list):
    """Convert concerts to ATOM format"""
    output = fg.Atom1Feed(title = 'Metalfinder',
                          description = 'Feed for your personalised concerts',
                          link = 'https://gitlab.com/baldurmen/metalfinder',
                          language = 'en')
    # This is needed for new concerts to be at the top of the ATOM file
    concert_list = sorted(concert_list,
                          key=lambda concert: concert['updated'],
                          reverse=True)
    for concert in concert_list:
        event_id, artists, date, venue, description, url = pretty_strings(concert)
        output.add_item(title = f"{artists} @ {venue} on {date}",
                        link = url,
                        content = description,
                        description = description,
                        unique_id = event_id,
                        pubdate = concert['updated'])
    return output


def txt(concert_list):
    """Convert concerts to text format"""
    output = ''
    for concert in concert_list:
        dummy, artists, date, venue, description, url = pretty_strings(concert)
        output += ('\n'
                   f'Artists: {artists},\n'
                   f'Date: {date},\n'
                   f'Venue: {venue},\n'
                   f'Description: {description}\n'
                   f'Link: {url},\n'
                   '\n'
                   '===============================================================\n')
    return output


def _json(concert_list):
    """Convert concerts to JSON format"""
    output = []
    for concert in concert_list:
        event_id, artists, date, venue, description, url = pretty_strings(concert)
        output.append({"eventId": event_id, "artists": artists, "date": date,
                       "venue": venue, "description": description, "link": url})
    output = json.dumps(output)
    return output


def output_wrapper(concert_list, output_path):
    """Wrapper function to manage the output"""
    extension = os.path.splitext(output_path)[1][1:]
    if extension == 'atom':
        output = atom(concert_list)
        with open(output_path, 'w', encoding='utf-8') as final:
            output.write(final, 'utf-8')
    else:
        if extension == 'txt':
            output = txt(concert_list)
        if extension == 'json':
            output = _json(concert_list)
        with open(output_path, 'w', encoding='utf-8') as final:
            final.write(output)
