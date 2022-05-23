# coding=utf-8
from __future__ import absolute_import, print_function

import requests

from suanpan import asyncio, debug
from suanpan.utils import term

DEFAULT_MARK_PERCENTAGES = (0.5, 0.66, 0.75, 0.8, 0.9, 0.95, 0.98, 0.99, 1)


roundns = lambda s: round(s * 1000, 3)


def printResponseTime(results, markPercentages=DEFAULT_MARK_PERCENTAGES):
    number = len(results)
    costTimes = sorted(
        ({"total": r[0], "response": r[1].elapsed.total_seconds()} for r in results),
        key=lambda t: t["response"],
    )
    responseTimes = [t["response"] for t in costTimes]
    sumTime = sum(responseTimes)
    avgTime = sumTime / number
    minTime = min(responseTimes)
    maxTime = max(responseTimes)

    print()
    term.table(
        [
            ["Response Time:"],
            ["---"],
            ["Sum", f"{roundns(sumTime)}ms"],
            ["Average", f"{roundns(avgTime)}ms"],
            ["Min", f"{roundns(minTime)}ms"],
            ["Max", f"{roundns(maxTime)}ms"],
        ]
    )

    print()
    print("Percentage of the requests served within a certain time:")
    print("---")
    term.table(
        [
            [
                f"{int(mp * 100)}%",
                f"{roundns(costTimes[int(number * mp) - 1]['total'])}ms",
                f"{roundns(costTimes[int(number * mp) - 1]['response'])}ms",
            ]
            for mp in markPercentages
        ],
        headers=["", "Total", "Response"],
    )

    return results


def test(
    func,
    number,
    args=None,
    kwargs=None,
    title="ABTest",
    funcName=None,
    markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = args or []
    kwargs = kwargs or {}
    testFunc = lambda x: debug.costCall(func, *args, **kwargs)
    funcName = funcName or func.__name__
    func.__name__ = funcName
    totalTime, results = debug.costCall(
        asyncio.map, testFunc, range(number), pbar=title,
    )
    costTimes = sorted(r[0] for r in results)
    sumTime = sum(costTimes)
    avgTime = sumTime / number
    minTime = min(costTimes)
    maxTime = max(costTimes)

    print()
    print(title)
    print(debug.formatFuncCall(func, *args, **kwargs))
    print("---")
    term.table(
        [
            ["GEVENT"],
            ["Number", number],
            [],
            ["Cost Time:"],
            ["Total", f"{roundns(totalTime)}ms"],
            ["Sum", f"{roundns(sumTime)}ms"],
            ["Average", f"{roundns(avgTime)}ms"],
            ["Min", f"{roundns(minTime)}ms"],
            ["Max", f"{roundns(maxTime)}ms"],
        ]
    )

    print()
    print("Percentage of the tests served within a certain time:")
    print("---")
    term.table(
        [
            [f"{int(mp * 100)}%", f"{roundns(costTimes[int(number * mp) - 1])}ms"]
            for mp in markPercentages
        ]
    )

    return {
        "results": results,
        "cost": {
            "total": totalTime,
            "average": avgTime,
            "min": minTime,
            "max": maxTime,
        },
    }


def request(
    method, url, number, kwargs=None, markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = [method, url]
    result = test(
        requests.request,
        number=number,
        args=args,
        kwargs=kwargs,
        title=f"ABTest - Request - {method.upper()}",
        markPercentages=markPercentages,
    )
    printResponseTime(result["results"], markPercentages=markPercentages)
    return result


def get(
    url, number, params=None, kwargs=None, markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = [url]
    kwargs = kwargs or {}
    kwargs.update(params=params)
    result = test(
        requests.get,
        number=number,
        args=args,
        kwargs=kwargs,
        title="ABTest - Request - GET",
        markPercentages=markPercentages,
    )
    printResponseTime(result["results"], markPercentages=markPercentages)
    return result


def post(
    url,
    number,
    data=None,
    json=None,
    kwargs=None,
    markPercentages=DEFAULT_MARK_PERCENTAGES,
):
    args = [url]
    kwargs = kwargs or {}
    kwargs.update(data=data, json=json)
    result = test(
        requests.post,
        number=number,
        args=args,
        kwargs=kwargs,
        title="ABTest - Request - POST",
        markPercentages=markPercentages,
    )
    printResponseTime(result["results"], markPercentages=markPercentages)
    return result
