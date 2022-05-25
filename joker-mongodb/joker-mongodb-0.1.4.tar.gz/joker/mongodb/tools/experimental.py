#!/usr/bin/env python3
# coding: utf-8

from gridfs import GridFS


def _get_gridfs_namespace(fs: GridFS):
    coll = getattr(fs, '_GridFS__files')
    db = coll.database
    return f'{db.name}.{coll.name}'

