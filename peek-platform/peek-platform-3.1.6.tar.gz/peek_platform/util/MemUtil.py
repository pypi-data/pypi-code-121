import logging
import tracemalloc
from datetime import datetime
from tracemalloc import _format_size
from typing import Optional

from twisted.internet import reactor
from twisted.internet.threads import deferToThread

logger = logging.getLogger(__name__)


def rpad(val, count):
    val = str(val)
    return val + max(0, (count - len(val))) * " "


def lpad(val, count):
    val = str(val)
    return max(0, (count - len(val))) * " " + val


def center(val, width=80):
    return max(0, int((width - len(val)) / 2)) * " " + val


PEEK_MEM_DUMP_STACKTRACE = 2 ** 0  # 1
PEEK_MEM_DUMP_VORTEX_OBSERVABLE_CACHE = 2 ** 2  # 2
PEEK_MEM_DUMP_VORTEX_JSONABLE = 2 ** 3  # 4
PEEK_MEM_DUMP_VORTEX_PUSH_PRODUCER = 2 ** 4  # 8


def _formatTracemallocTraceback(top, size, count):
    sitePkgs = "site-packages"

    snapshot = tracemalloc.take_snapshot()

    # Get the objects by their line of malloc
    tracebackStats = list(
        filter(
            lambda s: s.size > size or s.count > count, snapshot.statistics("traceback")
        )
    )[:top]

    text = "The traceback module is using %s memory\n" % _format_size(
        tracemalloc.get_tracemalloc_memory(), False
    )

    if not tracebackStats:
        text += "There are no large tracemalloc objects from traceback\n"
        return text

    text += "\n"

    # ---------------
    # Print the traceback summary

    for stat in tracebackStats:
        average = stat.size / stat.count

        tracePath = str(stat.traceback)
        if sitePkgs in tracePath:
            tracePath = tracePath[tracePath.index(sitePkgs) + len(sitePkgs) + 1 :]

        text += "   size:%s" % lpad(_format_size(stat.size, False), 10)
        text += "   count:%s" % lpad(stat.count, 10)
        text += "   average:%s" % lpad(_format_size(average, False), 10)
        text += "   " + tracePath

        text += "\n"

        for line in stat.traceback.format():
            text += (" " * 8) + line + "\n"

        text += "\n"

    # ---------------
    # Print the lineno summary

    text += (
        " "
        + rpad("COUNT", 10)
        + " "
        + rpad("SIZE", 10)
        + " "
        + rpad("AVERAGE", 10)
        + " "
        + "MALLOC LINE"
        + "\n"
    )

    for stat in tracebackStats:
        average = stat.size / stat.count

        tracePath = str(stat.traceback)
        if sitePkgs in tracePath:
            tracePath = tracePath[tracePath.index(sitePkgs) + len(sitePkgs) + 1 :]

        text += (
            " "
            + rpad(str(stat.count), 10)
            + " "
            + rpad(_format_size(stat.size, False), 10)
            + " "
            + rpad(_format_size(average, False), 10)
            + " "
            + tracePath
            + "\n"
        )

    text += "\n"

    return text


def _formatJsonableSummary(top, size):
    from vortex.Jsonable import Jsonable

    jsonableDump = Jsonable.memoryLoggingDump(top=top, over=size)

    if not jsonableDump:
        return "There are no large Vortex Jsonable Objects\n"

    text = " " + rpad("COUNT", 10) + " " + "OBJECT TYPE" + "\n"
    for objectType, count in jsonableDump:
        text += " " + rpad(str(count), 10) + " " + objectType + "\n"

    return text


def _formatObservableCacheSummary(top, size):
    from vortex.handler.TupleDataObservableCache import _CachedSubscribedData

    vortexCacheDump = _CachedSubscribedData.memoryLoggingDump(top=top, over=size)

    if not vortexCacheDump:
        return "There are no large Vortex Observable Caches\n"

    text = (
        " "
        + rpad("QUEUE ITEMS", 10)
        + " "
        + rpad("TOTAL SIZE", 10)
        + " "
        + "REMOTE VORTEX"
        + "\n"
    )

    for objectType, count, total in vortexCacheDump:
        text += (
            " "
            + rpad(str(count), 10)
            + " "
            + rpad(str(total), 10)
            + " "
            + objectType
            + "\n"
        )

    return text


def _formatVortexPushProducerSummary(top, msgs):
    from vortex.VortexWritePushProducer import VortexWritePushProducer

    stats = VortexWritePushProducer.memoryLoggingDump(top=top, msgs=msgs)

    if not stats:
        return "There are no large producer queues\n"

    text = (
        " " + rpad("MSGS", 10) + " " + rpad("TOTAL", 10) + " " + "REMOTE VORTEX" + "\n"
    )

    for objectType, count, total in stats:
        text += (
            " "
            + rpad(str(count), 10)
            + " "
            + rpad(str(total), 10)
            + " "
            + objectType
            + "\n"
        )

    return text


def setupMemoryDebugging(serviceName: Optional[str] = None, debugMask: int = 0):
    import os
    import pytz
    import psutil

    TRACEMALLOC_STACK_SIZE = 6

    class _State:
        lastClearDate = datetime.now(pytz.utc)

    # Start tracemalloc logging
    if debugMask & PEEK_MEM_DUMP_STACKTRACE:
        tracemalloc.start(TRACEMALLOC_STACK_SIZE)

    # Start JSonable logging
    from vortex.Jsonable import Jsonable

    if debugMask & PEEK_MEM_DUMP_VORTEX_JSONABLE:
        Jsonable.setupMemoryLogging()

    from vortex.handler.TupleDataObservableCache import _CachedSubscribedData

    if debugMask & PEEK_MEM_DUMP_VORTEX_OBSERVABLE_CACHE:
        # Start cached encoded payload logging
        _CachedSubscribedData.setupMemoryLogging()

    from vortex.VortexWritePushProducer import VortexWritePushProducer

    if debugMask & PEEK_MEM_DUMP_VORTEX_PUSH_PRODUCER:
        # Start cached encoded payload logging
        VortexWritePushProducer.setupMemoryLogging()

    TOP = 10
    COUNT_MIN = 10000
    TOTAL_SIZE = 1 * 1024 * 1024
    INDIVIDUAL_SIZE = 10 * 1024

    logger.warning("Memory Logging is enabled.")

    def dump():
        startTime = datetime.now(pytz.utc)

        # This is useful for debugging c binding memory leaks
        # roots = objgraph.get_leaking_objects()
        # objgraph.show_refs(roots[:3], refcounts=True, filename='/Users/peek/stash/roots.png')

        flushRequired = 3600 < (datetime.now(pytz.utc) - _State.lastClearDate).seconds
        if flushRequired:
            _State.lastClearDate = datetime.now(pytz.utc)

        homeDir = os.path.expanduser("~/memdump-%s.log" % serviceName)
        with open(homeDir, "a") as f:

            # Write the start datetime
            f.write("=" * 80 + "\n")
            f.write("START - " + str(startTime) + "\n")

            if flushRequired:
                f.write("THE HOURLY FLUSH OCCURRED\n")

            # Write the total process memory
            f.write("-" * 80 + "\n")
            process = psutil.Process(os.getpid())
            f.write(
                "Total python processes memory usage: "
                + rpad(_format_size(process.memory_info().rss, False), 10)
                + "\n"
            )

            if debugMask & PEEK_MEM_DUMP_STACKTRACE:
                if flushRequired:
                    tracemalloc.stop()
                    tracemalloc.start(TRACEMALLOC_STACK_SIZE)

                f.write("-" * 80 + "\n")
                f.write(center("Python Tracemalloc Information") + "\n")
                f.write(_formatTracemallocTraceback(TOP, TOTAL_SIZE, COUNT_MIN))

            if debugMask & PEEK_MEM_DUMP_VORTEX_JSONABLE:
                # Write the dump of the Jsonable objects
                f.write("-" * 80 + "\n")
                f.write(center("Vortex Jsonable Objects") + "\n")
                f.write(_formatJsonableSummary(TOP, INDIVIDUAL_SIZE))

            if debugMask & PEEK_MEM_DUMP_VORTEX_OBSERVABLE_CACHE:
                # Write the dump of the cached vortex payloads
                f.write("-" * 80 + "\n")
                f.write(center("Vortex Observable Caches") + "\n")
                f.write(_formatObservableCacheSummary(TOP, INDIVIDUAL_SIZE))

            if debugMask & PEEK_MEM_DUMP_VORTEX_PUSH_PRODUCER:
                # Write the dump of the cached vortex payloads
                f.write("-" * 80 + "\n")
                f.write(center("Vortex Write Push Producer") + "\n")
                f.write(_formatVortexPushProducerSummary(10, 1))

            # Write the end date
            f.write("-" * 80 + "\n")
            f.write(
                "END - Time taken : %s seconds"
                % str(datetime.now(pytz.utc) - startTime)
                + "\n"
            )
            f.write("-" * 80 + "\n")

        reactor.callLater(60, deferToThread, dump)

    dump()
