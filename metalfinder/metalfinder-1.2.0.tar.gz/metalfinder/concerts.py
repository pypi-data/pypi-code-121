#!/usr/bin/python3

"""
get concerts data from API provider
"""

import os
import pickle
import datetime

from .api.bandsintown import Client


def has_changed(concert_cache, concert):
    """Query concert cache to know if concert has changed (or is new) since
    last run."""
    concert_is_new = False
    if not any(concert['id'] in item['id'] for item in concert_cache):
        concert_is_new = True
    return concert_is_new


def write_concert_cache(data, cache_dir):
    """Write concert cache file to disk"""
    concert_cache_file = os.path.join(cache_dir, 'concert_cache')
    with open(concert_cache_file, 'wb') as _cache:
        pickle.dump(data, _cache)


def get_concert_cache(cache_dir):
    """Get the concert cache if it exists"""
    concert_cache = []
    concert_cache_file = os.path.join(cache_dir, 'concert_cache')
    if os.path.isfile(concert_cache_file):
        with open(concert_cache_file, 'rb') as _cache:
            concert_cache = pickle.load(_cache)
    return concert_cache


def query_bit(raw_artists, args):
    """Query Bandsintown for concert list"""
    bit_client = Client(args.bit_appid)
    concert_list = []
    for artist in raw_artists:
        # TODO: Why are we getting some empty artists?
        if artist != '':
            if args.max_date:
                date_range = str(datetime.date.today()) + ',' + args.max_date
                concerts = bit_client.artists_events(artist, date=date_range)
            else:
                concerts = bit_client.artists_events(artist)
            if concerts is not None:
                concert_list = concert_list + concerts
    return concert_list


def filter_location(concert_list, location):
    """Filter concerts based on location"""
    concert_list = [concert for concert in concert_list if
            (concert['venue']['city'] == location)]
    return concert_list


def bit(raw_artists, args):
    """Wrapper function for Bandsintown provider"""
    concert_cache = get_concert_cache(args.cache_dir)
    concert_list = query_bit(raw_artists, args)
    concert_list = filter_location(concert_list, args.location)
    for concert in concert_list:
        if has_changed(concert_cache, concert):
            concert['updated'] = datetime.datetime.now()
            concert_cache.append(concert)
    write_concert_cache(concert_cache, args.cache_dir)
    return concert_cache
