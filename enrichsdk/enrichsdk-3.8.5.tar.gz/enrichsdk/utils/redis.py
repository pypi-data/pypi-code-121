"""
Redis integration.

"""
import traceback
import json
import pickle
from collections import defaultdict

# Good use of the iterator and del command
# https://stackoverflow.com/questions/21975228/redis-python-how-to-delete-all-keys-according-to-a-specific-pattern-in-python


def bulk_get_data(cache, keys):
    """
    Get the data for keys...
    :param keys: list, list of keys
    :return: list, data at keys
    """

    data = []

    if len(keys) > 0:
        pipe = cache.pipeline()
        for k in keys:
            pipe.hgetall(k)
        data = pipe.execute()

    return data


def bulk_get_keys(cache, pattern, chunk_size=5000):
    """
    Get the keys...
    :param ns: str, namespace i.e your:prefix
    :return: int, cleared keys
    """

    allkeys = []
    cursor = "0"
    while cursor != 0:
        cursor, keys = cache.scan(cursor=cursor, match=pattern, count=chunk_size)
        if keys:
            allkeys.extend(keys)

    return allkeys


def clear(cache, pattern, chunk_size=5000):
    """
    Clears a namespace
    :param ns: str, namespace i.e your:prefix
    :return: int, cleared keys
    """

    count = 0
    cursor = "0"
    while cursor != 0:
        cursor, keys = cache.scan(cursor=cursor, match=pattern, count=chunk_size)
        if keys:
            count += len(keys)
            cache.delete(*keys)

    return count


def clear_atomic(cache, pattern):
    """
    Clears a namespace in redis cache.
    This may be very time consuming.
    :param pattern: str, namespace i.e your:prefix*
    :return: int, num cleared keys
    """
    count = 0
    pipe = cache.pipeline()
    for key in cache.scan_iter(ns):
        pipe.delete(key)
        count += 1
    pipe.execute()

    return count


def write_records_atomic(cache, records, keygenerator, spec, expiry=7 * 86400):
    """
    Serialize and write records

    :param records: list of dictionaries
    :param keygenerator: generates key from dict
    :param spec: what should this function do?
    :return: stats, stats about the redis write

    """

    error = 0
    count = 0
    found = defaultdict(int)
    stats = defaultdict(int)

    exclude = spec.get("exclude", [])  # what columns to exclude
    suffix = spec.get("suffix", "")  # add bits to the key name
    target = spec.get("target", "map")  # what is the target

    # Make sure we know what action to do.
    # map = store a dict
    # map-serialized: serialize the dict and store
    # elements = store individual elements
    # elements-serialized = store individual elements but serialize them..
    #
    if target not in ["map", "map-serialized", "elements", "elements-serialized"]:
        raise Exception(f"Unknown target: {target}")

    if not isinstance(exclude, list):
        raise Exception(f"Unknown type of exclude {type(exclude)}")

    pipe = cache.pipeline()
    for r in records:

        try:

            # First generate the key using the entire record
            if isinstance(keygenerator, str):
                key = keygenerator % r
            elif callable(keygenerator):
                key = keygenerator(r)
            else:
                raise Exception("Unknown key generator")

            # What are the available columns?
            columns = spec.get("columns", list(r.keys()))

            # What should I exclude?
            columns = [c for c in columns if c not in exclude]

            # Get what I should write
            towrite = {k: v for k, v in r.items() if k in columns}

            if len(towrite) == 0:
                stats["error-empty"] += 1
                continue

            # Handle the simple cases...
            if spec["target"] in ["map", "map-serialized"]:
                key += suffix
                if key in found:
                    stats["duplicates"] += 1
                    continue
                if target == "map-serialized":  # serialize
                    value = pickle.dumps(towrite)
                    pipe.set(key + "_pickled", value)
                else:
                    pipe.hmset(key, towrite)
                found[key] = 1

                # In all cases set the expiry...
                if expiry > 0:
                    pipe.expire(key, expiry)

                stats["valid"] += 1
                continue

            # Handle the list case...
            if spec["target"] in ["elements", "elements-serialized"]:
                for col in list(towrite.keys()):
                    colkey = f"{key}:{col}{suffix}"
                    # Have we seen this key?
                    if colkey in found:
                        stats["duplicates"] += 1
                        continue

                    value = towrite[col]

                    # We now have to set the list...
                    if target == "elements-serialized":
                        value = pickle.dumps(value)
                        pipe.set(colkey + "_pickled", value)
                    elif isinstance(value, list):
                        pipe.delete(colkey)  # clear all elements
                        pipe.rpush(colkey, *value)
                    elif isinstance(value, dict):
                        pipe.hmset(colkey, value)
                    else:
                        raise Exception(
                            f"Unknown element type {type(value)} for {colkey}"
                        )

                    found[colkey] += 1
                    stats["valid"] += 1

        except Exception as e:
            stats["error"] += 1
            stats["message"] = str(e)
            break

        count += 1

    pipe.execute()

    return dict(stats)


def write_df_dict(cache, df, keygenerator, spec, expiry=7 * 86400):
    """
    Serialize and write dataframe

    :param df: dataframe to write
    :param keygenerator: generates key from dict
    :param spec: how should the dict be handled?
    :param expiry: expiry in seconds (default 7 days)
    :return: stats, stats about the redis write

    Write selected columns
    spec = {
        "target": "map",
        "columns": ["key1", "key2"]
    ]

    Write selected columns but serialize them if they
    are not of the standard datatype
    spec = {
        "target": "map-serialized",
        "columns": ["key1", "key2"]
    ]


    Write each of the columns to a separate key
    spec = {
        "target": "elements",
        "columns": ["key1", "key2"]
    ]


    """

    # Generate records
    records = df.to_dict("records")

    return write_records_atomic(cache, records, keygenerator, spec, expiry)
