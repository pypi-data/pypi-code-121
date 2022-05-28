#!/usr/bin/python3

"""Unit tests for metalfinder.scan"""

from metalfinder.scan import scan_wrapper


def test_scan_broken_symlink(tmpdir):
    """test that we don't crash on broken symlinks (issues #21)"""
    cachedir = tmpdir.join("cache")
    cachedir.mkdir()
    musicdir = tmpdir.join("music")
    musicdir.mkdir()
    musicdir.join("brokensymlink.mp3").mksymlinkto("nonexistent")
    # we don't actually need the result here
    _ = scan_wrapper(musicdir, cachedir)
