#!/usr/bin/env python3
# coding: utf-8

from pymongo.collection import Collection


def _namemap_to_project(namemap: dict):
    project = {}
    for new_name, old_name in namemap.items():
        if not old_name.startswith('$'):
            old_name = '$' + old_name
        project[new_name] = {'$ifNull': [old_name, None]}
    return project


def _namemap_from_fieldlist(fieldlist: list):
    return {k.split('.')[-1]: k for k in fieldlist}


def find_with_renaming(
        coll: Collection, filtr: dict, namemap: dict, sort: dict = None):
    pipelines = [
        {'$match': filtr},
        {'$sort': sort or {'_id': -1}},
        {'$project': _namemap_to_project(namemap)},
    ]
    return coll.aggregate(pipelines)


def find_one_with_renaming(
        coll: Collection, filtr: dict, namemap: dict, sort: dict = None):
    pipelines = [
        {'$match': filtr},
        {'$sort': sort or {'_id': -1}},
        {'$limit': 1},
        {'$project': _namemap_to_project(namemap)},
    ]
    docs = list(coll.aggregate(pipelines))
    if docs:
        return docs[0]
