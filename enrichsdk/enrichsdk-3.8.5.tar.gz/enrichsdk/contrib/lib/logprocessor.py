import json
import sqlite3
import logging
import traceback
import re
import time
from sqllineage.runner import LineageRunner

from dateutil import parser as dateparser
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger("app")

#######################################
class StorageBase(object):
    def __init__(self, config, *args, **kwargs):
        self.config = config


class SQLiteStorage(StorageBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "SQLite"

        if "db" not in self.config:
            raise Exception("db should be specified")

        self.initialize()

    def initialize(self):

        con = sqlite3.connect(self.config["db"])
        cursor = con.cursor()
        sql = """
CREATE TABLE IF NOT EXISTS raw (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     loggroup TEXT NOT NULL,
     logstream TEXT NOT NULL,
     lastevent BIGINT,
     timestamp BIGINT,
     message TEXT NOT NULL
)
        """

        cursor.execute(sql)

        sql = """
CREATE TABLE IF NOT EXISTS processed (
     id INTEGER PRIMARY KEY AUTOINCREMENT,
     loggroup text NOT NULL,
     logstream TEXT NOT NULL,
     lastevent BIGINT,
     timestamp DATETIME,
     level VARCHAR(256),
     path VARCHAR(256),
     lineno VARCHAR(256),
     method VARCHAR(128),
     message TEXT NOT NULL,
     metadata TEXT
)
        """
        cursor.execute(sql)
        con.close()

    def check(self, table, group, stream, lastevent):

        con = sqlite3.connect(self.config["db"])

        sql = f"""\
SELECT count(1)
FROM {table}
WHERE ((loggroup = '{group}') AND (logstream = '{stream}') and (lastevent = '{lastevent}'))
        """

        cursor = con.cursor()
        cursor.execute(sql)
        rows = cur.fetchall()
        count = rows[0][0]
        con.close()

        return count > 0

    def get_lastevent(self, table, group, stream):

        con = sqlite3.connect(self.config["db"])

        sql = f"""\
select DISTINCT lastevent
FROM {table}
WHERE ((loggroup = '{group}') AND (logstream = '{stream}'))
        """

        cursor = con.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        lastevent = rows[0][0] if len(rows) > 0 else None
        con.close()
        return lastevent

    def clear(self, table, group, stream):

        con = sqlite3.connect(self.config["db"])

        sql = f"""\
DELETE
FROM {table}
WHERE ((loggroup = '{group}') AND (logstream = '{stream}'))
        """
        cursor = con.cursor()
        cursor.execute(sql)
        con.commit()
        con.close()
        return

    def insert(self, table, group, stream, lastevent, events):

        con = sqlite3.connect(self.config["db"])

        # => Construct the values...
        cols = ["timestamp", "level", "path", "lineno", "method", "message", "metadata"]
        values = []
        for e in events:
            v = [group, stream, lastevent]
            for col in cols:
                v.append(e[col])
            values.append(v)

        # construct sql
        sql = f"""\
INSERT INTO {table}( loggroup, logstream, lastevent, timestamp, level, path, lineno, method, message, metadata)
VALUES (?, ?, ?, ?,?, ?, ?, ?,?,?)
        """
        cursor = con.cursor()
        cursor.executemany(sql, values)
        con.commit()
        con.close()


######################################
#
######################################
class TaggerBase(object):
    def __init__(self, config, *args, **kwargs):
        self.config = config


class RegexTagger(TaggerBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "RegexTagger"

    def tag(self, event):

        rules = self.config["rules"]

        message = event["message"]
        tags = []
        for tagname, patterns in rules.items():
            for p in patterns:
                match = re.search(p, message, re.IGNORECASE)
                if match is not None:
                    tags.append(tagname)
                    break
        if len(tags) == 0:
            tags.append("no-tag")
        return tags


class MetadataBase(object):
    def __init__(self, config, *args, **kwargs):
        self.config = config

    def process(self, event):
        return {}


class DBTLineageMetadata(MetadataBase):
    def process(self, event):

        message = event["message"]

        if not ((re.search("On \S+:", message)) and ('"app": "dbt"' in message)):
            return {}

        lines = message.split("\n")

        # First compute the SQL
        sql = ""
        join = False
        for idx, m in enumerate(lines):
            if (re.match("^On \S+:", m)) and ('"app": "dbt"' in m):
                join = True
                continue
            if join:
                sql += "\n" + m

        update = {}
        if len(sql) == 0:
            return update

        try:
            result = LineageRunner(sql, verbose=True)
            update = {
                "lineage": {
                    "status": "success",
                    "source_tables": [str(t) for t in result.source_tables],
                    "target_tables": [str(t) for t in result.target_tables],
                    "intermediate_tables": [str(t) for t in result.intermediate_tables],
                    "column_lineage": result.get_column_lineage(),
                }
            }

        except:
            update = {
                "lineage": {"status": "failure", "exception": traceback.format_exc()}
            }

        return update


class ProcessorBase(object):
    pass


class CloudwatchProcessor(ProcessorBase):
    def __init__(self, *args, **kwargs):
        self.name = "Cloudwatch"

    def get_streams(self, spec):

        client = spec["args"]["client"]
        log_group = spec["log_group"]

        # What is the cutoff
        cutoff = dateparser.parse(spec.get("cutoff", "1970-01-01"))
        cutoff = (cutoff - datetime(1970, 1, 1)).total_seconds()

        msg = ""
        allstreams = []
        next_token = None
        iteration = 1
        max_iterations = 100
        while iteration < max_iterations:
            try:
                params = {"nextToken": next_token} if next_token is not None else {}
                response = client.describe_log_streams(
                    logGroupName=log_group,
                    orderBy="LastEventTime",
                    descending=True,
                    limit=50,
                    **params,
                )

                # Get all the streams
                streams = response["logStreams"]
                numstreams = len(streams)

                # Now filter out older ones
                streams = [
                    s for s in streams if (s["firstEventTimestamp"] / 1000) >= cutoff
                ]
                netstreams = len(streams)
                msg += f"[{iteration}] {numstreams} -> {netstreams}\n"

                if netstreams == 0:
                    break

                allstreams.extend(streams)
                next_token = response["nextToken"]

                # Some records have been filtered, i.e., we
                # cross the cutoff
                if netstreams < numstreams:
                    break

                iteration += 1
            except:
                logger.exception(
                    f"Failed {log_group}", extra={"transform": self.name, "data": msg}
                )
                raise

        msg += f"[Completed] {len(allstreams)}"
        logger.debug(
            f"[{log_group}] {len(allstreams)} streams",
            extra={"transform": self.name, "data": msg},
        )

        return allstreams

    def get_logs(self, spec, stream):

        """
        {
             "logStreamName": "ecs/trip-recommender-api/3c4f22c7e0444331973bc040ce577265",
             "creationTime": 1637033546947,
             "firstEventTimestamp": 1637033588852,
             "lastEventTimestamp": 1637033589298,
             "lastIngestionTime": 1637033592949,
             "uploadSequenceToken": "49605172774206290057587551428896880961727365107853296162",
             "arn": "arn:aws:logs:eu-west-1:441203537012:log-group:/ecs/trip-recommender-api:log-stream:ecs/trip-recommender-api/3c4f22c7e0444331973bc040ce577265",
             "storedBytes": 0
         },
        """

        client = spec["args"]["client"]
        db = spec["args"]["db"]

        # What is the cutoff
        cutoff = dateparser.parse(spec.get("cutoff", "1970-01-01"))
        cutoff = (cutoff - datetime(1970, 1, 1)).total_seconds()

        specname = spec["name"]
        log_group = spec["log_group"]
        log_stream = stream["logStreamName"]
        created = stream["creationTime"]
        start_time = max(stream["firstEventTimestamp"], cutoff)
        lastevent_timestamp = stream["lastEventTimestamp"]
        name = stream["logStreamName"]
        force = spec.get("force", False)

        # Get existing last event
        db_lastevent = db.get_lastevent("processed", log_group, log_stream)
        msg = f"[DB] Last event: {db_lastevent} {type(db_lastevent)}\n"
        msg += (
            f"[Stream] Last event: {lastevent_timestamp} {type(lastevent_timestamp)} ("
            + ("Match" if (db_lastevent == lastevent_timestamp) else "No match")
            + ")\n"
        )
        msg += f"[Force] {force}\n"

        # Exists and valid..
        if (
            (db_lastevent is not None)
            and (db_lastevent == lastevent_timestamp)
            and (not force)
        ):
            msg += "Skipping. Updated"
            logger.debug(
                f"[{log_stream[-32:]}] Skipping",
                extra={"transform": self.name, "data": msg},
            )
            return None

        # Clear all previous events
        if db_lastevent is not None:
            msg += "Clearing db\n"
            db.clear("processed", log_group, log_stream)

        allevents = []
        iteration = 1
        next_token = None
        max_iterations = 5 if spec.get("test", False) else 10000
        while iteration < max_iterations:
            try:
                params = {"nextToken": next_token} if next_token is not None else {}
                response = client.get_log_events(
                    logGroupName=log_group,
                    logStreamName=log_stream,
                    startTime=start_time,
                    endTime=lastevent_timestamp,
                    startFromHead=False,
                    limit=2000,
                    **params,
                )

                events = response["events"]
                allevents.extend(events)
                if len(events) == 0:
                    break

                iteration += 1
                next_token = response["nextBackwardToken"]

                msg += (
                    f"Iteration: {iteration} new {len(events)} Total {len(allevents)}\n"
                )

            except:
                logger.exception(
                    f"Failed {log_stream[-32:]}",
                    extra={
                        "transform": self.name,
                    },
                )
                raise

        logger.debug(
            f"[{log_stream[-32:]}] {len(allevents)} events",
            extra={"transform": self.name, "data": msg},
        )

        return allevents

    def collapse_events(self, spec, stream, allevents):
        """
        Take the raw events and process them...
        """

        db = spec["args"]["db"]
        specname = spec["name"]
        regexps = spec["regexps"]
        if isinstance(regexps, str):
            regexps = [regexps]
        log_group = spec["log_group"]
        log_stream = stream["logStreamName"]

        created = stream["creationTime"]
        lastevent_timestamp = stream["lastEventTimestamp"]

        try:
            stats = defaultdict(int)
            cleaned = []
            lastevent = None
            for event in allevents:

                stats["total"] += 1
                timestamp = event["timestamp"]
                dt = datetime.utcfromtimestamp(timestamp / 1000)
                dt = dt.replace(microsecond=(timestamp % 1000) * 1000)

                message = event["message"]

                # 2022-01-21 11:04:19,106 loglevel=INFO   logger=src.matching load_s3_pickle() L45
                match = None
                for regexp in regexps:
                    match = re.match(regexp, message)
                    if match is not None:
                        break

                parsedevent = None
                if match is not None:
                    stats["parsed"] += 1
                    parsedevent = match.groupdict()

                    # Use the log timestamp consistently. This differs from the log timestamp.
                    parsedevent["timestamp"] = dt.isoformat()
                    for col in ["path", "method", "lineno"]:
                        if col not in parsedevent:
                            parsedevent[col] = None

                defaultevent = {
                    "level": None,
                    "timestamp": dt.isoformat(),
                    "path": None,
                    "method": None,
                    "lineno": None,
                    "message": message,
                }

                # print("last event", lastevent)

                if parsedevent is not None:
                    if lastevent is not None:
                        cleaned.append(lastevent)
                    lastevent = parsedevent
                    stats["final"] += 1
                    continue
                elif lastevent is not None:
                    lastevent["message"] += "\n" + message
                    stats["collapsed"] += 1
                else:
                    stats["final"] += 1
                    lastevent = defaultevent

            if lastevent is not None:
                stats["final"] += 1
                cleaned.append(lastevent)

            filtered = []
            tagger = spec["args"]["tagger"]
            lastevent = None
            for event in cleaned:

                tags = tagger.tag(event)

                if "ignore" in tags:
                    stats["ignored"] += 1
                    continue

                event["metadata"] = {"tags": tags}

                # 2022-01-24T12:00:27.685000
                # Merge if the tags the same, within a min of the previous event
                if (
                    (lastevent is not None)
                    and (set(tags) == set(lastevent["metadata"]["tags"]))
                    and (event["timestamp"][:16] == lastevent["timestamp"][:16])
                ):
                    lastevent["message"] = (
                        event["message"] + "\n" + lastevent["message"]
                    )
                    stats["merged"] += 1
                    continue

                lastevent = event
                filtered.append(event)

            stats["final"] -= stats.get("ignored", 0)
            stats["final"] -= stats.get("merged", 0)

            for event in filtered:
                event["metadata"] = json.dumps(event["metadata"])

            db.insert("processed", log_group, log_stream, lastevent_timestamp, filtered)
            logger.debug(
                f"[{log_stream[-32:]}] processed",
                extra={"transform": self.name, "data": json.dumps(stats, indent=4)},
            )
        except:
            logger.exception(
                f"[{log_stream[-32:]}] failed",
                extra={"transform": self.name, "data": json.dumps(stats, indent=4)},
            )
            raise

    def run(self, spec):

        logger.debug(f"Processing {spec['name']}", extra={"data": str(spec)})

        streams = self.get_streams(spec)
        for stream in streams:
            try:
                allevents = self.get_logs(spec, stream)
                if (allevents is None) or (
                    isinstance(allevents, list) and len(allevents) == 0
                ):
                    continue

                self.collapse_events(spec, stream, allevents)

            except:
                logger.exception(f"Failed {stream['logStreamName']}")

        logger.debug(f"Completed {spec['name']}", extra={"data": str(spec)})


class S3DBTProcessor(ProcessorBase):
    def __init__(self, *args, **kwargs):
        self.name = "S3DBTProcessor"

    def process_one_file(self, spec, loggroup, f):

        s3 = spec["args"]["s3"]
        counts = defaultdict(int)
        regexps = spec["regexps"]

        # => Get the lines
        with s3.open(f, "r") as fd:
            lines = fd.readlines()
            lines = [l.rstrip() for l in lines]

        allstreams = {}
        logstream = None
        current_entry = None
        for line in lines:

            try:

                counts["lines"] += 1
                # First match the line and to see any regexp works
                for regexp in regexps:
                    match = re.match(regexp, line)
                    if match is not None:
                        break

                # Extract matched data. could be
                data = None if (match is None) else match.groupdict()

                if (logstream is None) or (
                    (data is not None) and ("streamname" in data)
                ):

                    # We havent seen the first line for the run
                    if match is None:
                        counts["nostream_nomatch"] += 1
                        continue

                    if "streamname" not in data:
                        counts["nostream_match_nodata"] += 1
                        continue

                    logstream = data["streamname"]
                    start_timestamp = dateparser.parse(data["timestamp"])
                    lastevent = (
                        time.mktime(start_timestamp.timetuple()) * 1e3
                        + start_timestamp.microsecond / 1e3
                    )

                    counts["stream_new"] += 1

                    # Now create a basic entry
                    allstreams[logstream] = {
                        "lastevent": lastevent,
                        "start_timestamp": start_timestamp,
                        "entries": [],
                    }
                    continue

                # =>We have logstream now. New entry
                start_timestamp = allstreams[logstream]["start_timestamp"]
                entries = allstreams[logstream]["entries"]
                if data is None:
                    if current_entry is not None:
                        current_entry["message"] += "\n" + line
                        counts["stream_merge"] += 1
                    else:
                        counts["stream_nocurrent_entry"] += 1
                    continue

                # New parsed entry with a timestamp. Store the old one
                if current_entry is not None:
                    entries.append(current_entry)
                    current_entry = None

                # Data is not None and logstream exists
                try:
                    # 05:36:37.028275 [info ] [MainThread]: Running with dbt=1.0.1
                    ts = dateparser.parse(data["timestamp"])
                    ts = ts.replace(
                        year=start_timestamp.year,
                        month=start_timestamp.month,
                        day=start_timestamp.day,
                    )
                    if ts < start_timestamp:
                        ts += timedelta(days=1)

                    level = data["level"]
                    message = data["message"]
                    counts["stream_newentry"] += 1
                    current_entry = {
                        "loggroup": loggroup,
                        "logstream": logstream,
                        "lastevent": lastevent,
                        "timestamp": ts.isoformat(),
                        "level": level,
                        "path": None,
                        "lineno": None,
                        "method": None,
                        "message": message,
                    }
                except:
                    traceback.print_exc()
                    counts["stream_invalid_entry"] += 1
                    raise
            except:
                logger.exception(f"{logstream} Unable to read")
                counts["stream_exception"] += 1
                raise

        if current_entry is not None and logstream is not None:
            allstreams[logstream]["entries"].append(current_entry)

        return allstreams, counts

    def run(self, spec):

        logger.debug(f"Processing {spec['name']}", extra={"data": str(spec)})

        log_group = spec["name"]
        db = spec["args"]["db"]
        s3 = spec["args"]["s3"]
        filepattern = spec["args"]["filepattern"]
        logstyle = spec["args"].get("logstyle", "default")

        if logstyle != "default":
            raise Exception(f"Unsupported logstyle. Only 'default' supported")

        # => Process all the files...
        files = s3.glob(filepattern)
        for idx, f in enumerate(files):
            allstreams, counts = self.process_one_file(spec, log_group, f)
            msg = f + "\n"
            msg += "Stats: " + json.dumps(counts, indent=4) + "\n"
            for logstream, detail in allstreams.items():
                msg += f"[{logstream}] {len(detail['entries'])}\n"
            logger.debug(f"[{log_group}] [{idx}] Processed", extra={"data": msg})

        # => Now tag and merge them...
        msg = ""
        tagger = spec["args"]["tagger"]
        for logstream in list(allstreams.keys()):

            entries = allstreams[logstream]["entries"]
            stats = defaultdict(int)

            # Tag and merge
            lastevent = None
            filtered = []
            for event in entries:

                stats["total"] += 1
                tags = tagger.tag(event)
                if "ignore" in tags:
                    stats["ignored"] += 1
                    continue
                event["metadata"] = {"tags": tags}

                if lastevent is None:
                    lastevent = event
                    filtered.append(event)
                    stats["new"] += 1
                    continue

                # 2022-01-24T12:00:27.685000
                # Merge if the tags the same, within a min of the previous event
                if (set(tags) == set(lastevent["metadata"]["tags"])) and (
                    event["timestamp"][:16] == lastevent["timestamp"][:16]
                ):
                    lastevent["message"] = (
                        event["message"] + "\n" + lastevent["message"]
                    )
                    stats["merged"] += 1
                    continue

                lastevent = event
                filtered.append(event)
                stats["new"] += 1

            if "metadata" in spec["args"]:
                metadata = spec["args"]["metadata"]
                for entry in filtered:
                    update = metadata.process(entry)
                    if len(update) > 0:
                        stats["nontag_metadata"] += 1
                        entry["metadata"].update(update)

            # Serialize entries...
            for entry in filtered:
                entry["metadata"] = json.dumps(entry["metadata"])

            # Now store it back...
            allstreams[logstream]["filtered"] = filtered
            msg += f"[{logstream}]\n" + json.dumps(stats, indent=4) + "\n"

        logger.debug("Tagged and merged", extra={"data": msg})
        # for event in filtered:
        #    print("-----")
        #   print(event['timestamp'])
        #  print(event['message'])

        # =>
        db = spec["args"]["db"]
        for log_stream, details in allstreams.items():
            filtered = details["filtered"]
            lastevent = details["lastevent"]
            db.clear("processed", log_group, log_stream)
            db.insert("processed", log_group, log_stream, lastevent, filtered)

        logger.debug(f"Completed {log_group}")
