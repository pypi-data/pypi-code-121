#!/usr/bin/python3

"""
scan a music directory and output a list of artists
"""

import logging
import os
import re
import pickle

import mutagen


def has_changed(song_cache, new_song_cache, fullpath):
    """Query song cache to know if file has changed (or is new) since last run.
    In any case, update the cache.

    Does not catch exceptions, can raise OS errors from os.stat."""
    file_changed = False
    mtime = os.stat(fullpath).st_mtime
    if (fullpath not in song_cache) or (fullpath in song_cache and
                                        song_cache[fullpath] != mtime):
        file_changed = True
    new_song_cache[fullpath] = mtime
    return new_song_cache, file_changed


def write_song_cache(data, cache_dir):
    """Write song cache file to disk"""
    song_cache_file = os.path.join(cache_dir, 'song_cache')
    with open(song_cache_file, 'wb') as _cache:
        pickle.dump(data, _cache)


def get_song_cache(cache_dir):
    """Get the song cache if it exists"""
    song_cache = {}
    song_cache_file = os.path.join(cache_dir, 'song_cache')
    if os.path.isfile(song_cache_file):
        with open(song_cache_file, 'rb') as _cache:
            song_cache = pickle.load(_cache)
    return song_cache


def write_artist_cache(data, cache_dir):
    """Write artist cache file to disk"""
    artist_cache_file = os.path.join(cache_dir, 'artist_cache')
    with open(artist_cache_file, 'w+', encoding='utf-8') as _cache:
        _cache.write('\n'.join(data))


def get_artist_cache(cache_dir):
    """Get the artist cache if it exists"""
    raw_artists = []
    artist_cache_file = os.path.join(cache_dir, 'artist_cache')
    if os.path.isfile(artist_cache_file):
        with open(artist_cache_file, 'r', encoding='utf-8') as _cache:
            raw_artists = _cache.read().splitlines()
    return raw_artists


def modify_artist(fullpath, raw_artists, action):
    """Modify artist list"""
    try:
        artist = mutagen.File(fullpath, easy=True)["artist"]
        artist = ''.join(artist)  # list to string
        split_pattern = re.compile(r"\+|/|&")
        if re.search(split_pattern, artist):
            splitted_artist = re.split(split_pattern, artist)
            for artist in splitted_artist:
                if action == 'add':
                    raw_artists.append(artist.lstrip())
                elif (action == 'remove') and (artist in raw_artists):
                    raw_artists.remove(artist.lstrip())
        else:
            if action == 'add':
                raw_artists.append(artist)
            elif (action == 'remove') and (artist in raw_artists):
                raw_artists.remove(artist)
    except KeyError:  # no artist tag
        pass
    except mutagen.flac.FLACNoHeaderError:  # FLAC file has no header
        pass
    return raw_artists


def scan_dir(music_dir, song_cache, raw_artists):
    """Scan a directory and output a list of artists"""
    new_song_cache = {}
    for dirname, _, filenames in os.walk(music_dir, topdown=False):
        for song in filenames:
            fullpath = os.path.abspath(os.path.join(dirname, song))
            if not song.endswith(('.flac', '.mp3', '.ogg')):
                continue
            try:
                new_song_cache, file_changed = has_changed(song_cache, new_song_cache, fullpath)
            except FileNotFoundError as _error:
                logging.warning("Could not load tags from file %s, skipping: %s", fullpath, _error)
                continue
            if file_changed:
                raw_artists = modify_artist(fullpath, raw_artists, 'add')
    stale_song_cache = set(song_cache) - set(new_song_cache)
    for song in stale_song_cache:
        raw_artists = modify_artist(song, raw_artists, 'remove')
    return set(raw_artists), new_song_cache


def scan_wrapper(music_dir, cache_dir):
    """Wrapper function to manage the scan"""
    raw_artists = get_artist_cache(cache_dir)
    if not music_dir:
        return raw_artists
    song_cache = get_song_cache(cache_dir)
    raw_artists, new_song_cache = scan_dir(music_dir, song_cache, raw_artists)
    write_song_cache(new_song_cache, cache_dir)
    write_artist_cache(raw_artists, cache_dir)
    return raw_artists
