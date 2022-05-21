from python_helper import Constant as c
from python_helper import ObjectHelper


def containsEmission(emissionList, emission):
    return (
        ObjectHelper.isNotNone(emissionList) and
        ObjectHelper.isNotNone(emission) and
        getKey(emission) in [getKey(e) for e in emissionList]
    )


def getKey(emission):
    return emission.key if ObjectHelper.isNotNone(emission.key) else buildKey(
        queueKey = emission.queueKey,
        subscriptionKey = emission.subscriptionKey,
        messageKey = emission.messageKey
    )


def buildKey(queueKey=None, subscriptionKey=None, messageKey=None):
    return f'{queueKey}{c.DOT}{subscriptionKey}{c.DOT}{messageKey}'
