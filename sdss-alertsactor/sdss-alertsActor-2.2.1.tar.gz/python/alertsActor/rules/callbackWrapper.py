#!/usr/bin/env python
# encoding: utf-8
#
# callbacks.py
#
# Created by John Donor on 9 Mar 2018.

import time
from opscore.RO.Comm.TwistedTimer import Timer

from alertsActor import log


class wrapCallbacks(object):
    """Pass in keywords read from a file
       along with their alert type.
    """

    def __init__(self, alertsActor, keywords):
        # keywords read from config
        self.alertsActor = alertsActor
        self.datamodel_casts = dict()
        self.datamodel_callbacks = dict()

        for key, actions in keywords.items():
            self.datamodel_casts[key] = actions['cast']

            initKeys = ('cast', 'severity', 'heartbeat', 'stale')

            otherArgs = {k: actions[k] for k in actions.keys() if k not in initKeys}

            if 'heartbeat' in actions.keys():
                alertKey = actions['heartbeat'] + '.heartbeat'
                self.alertsActor.addKey(alertKey,
                                        severity=actions['severity'],
                                        **otherArgs)
                callback = self.pulse(alertKey=alertKey,
                                      checkAfter=actions['checkAfter'])
                self.datamodel_callbacks[key] = callback

            elif 'stale' in actions.keys():
                staleKey = key + ".stale"
                self.alertsActor.addKey(staleKey, severity=actions['severity'],
                                        checkAfter=actions['stale'],
                                        selfClear=True,
                                        checker=staleCheck,
                                        instruments=actions['instruments'],
                                        emailAddresses=actions['emailAddresses'],
                                        emailDelay=actions.get('emailDelay', 120))

                alertKey = key
                self.alertsActor.addKey(alertKey,
                                        severity=actions['severity'],
                                        **otherArgs)

                requireChange = actions.get("requireChange", False)

                callback = self.updateKeyStale(key,
                                               checkAfter=actions['stale'],
                                               requireChange=requireChange)
                self.datamodel_callbacks[key] = callback

            else:
                alertKey = key
                self.alertsActor.addKey(alertKey,
                                        severity=actions['severity'],
                                        **otherArgs)
                callback = self.updateKey(key)
                self.datamodel_callbacks[key] = callback

            if "instruments" in actions.keys():
                for i in actions["instruments"]:
                    alertsActor.instrumentDown[i] = False

    def pulse(self, alertKey='NOT_SPECIFIED', checkAfter=30):
        """Update the heartbeat for a specified actor.
           The timer is restarted everytime its called, if it isn't restarted
           in time, a "dead actor" alert is raised
        """
        if alertKey not in self.alertsActor.heartbeats.keys():
            self.alertsActor.heartbeats[alertKey] = Timer()

        deadCallback = self.itsDeadJim(alertKey=alertKey)

        def startTime(newKeyval):
            # called as callback, so the updated key is passed by default
            # print('pulse: ', alertKey, newKeyval[0])
            log.info('{}: the actor said {}'.format(alertKey, newKeyval))
            # don't remember why we want the first element of the list here
            # but it shouldn't matter for heartbeat monitoring
            self.alertsActor.monitoring[alertKey].keyword = newKeyval[0]
            self.alertsActor.monitoring[alertKey].lastalive = time.time()
            self.alertsActor.heartbeats[alertKey].start(checkAfter, deadCallback)
            self.alertsActor.monitoring[alertKey].checkKey()

        startTime(["init"])  # call now so it raises error?

        return startTime

    def updateKeyStale(self, actorKey, checkAfter=30, requireChange=False):
        """Update the create a "stale" heartbeat for a specified actorKey.
           The timer is restarted everytime its called, if it isn't restarted
           in time, a "stale" alert is raised
        """
        staleKey = actorKey + ".stale"
        if staleKey not in self.alertsActor.heartbeats.keys():
            self.alertsActor.heartbeats[staleKey] = Timer()

        deadCallback = self.itsDeadJim(alertKey=staleKey)

        def check(newKeyval, init=False):
            if len(newKeyval) == 1:
                newKeyval = newKeyval[0]
            if init:
                self.alertsActor.monitoring[staleKey].keyword = 0
            if requireChange:
                # val has to change to reset timer, e.g. BPR
                # definitely don't want to do this for string keys
                if abs(self.alertsActor.monitoring[staleKey].keyword - newKeyval) < 0.1:
                    return None
            # also do the heartbeat
            self.alertsActor.monitoring[staleKey].keyword = newKeyval
            self.alertsActor.monitoring[staleKey].lastalive = time.time()
            self.alertsActor.heartbeats[staleKey].start(checkAfter, deadCallback)
            self.alertsActor.monitoring[staleKey].checkKey()

            if init:
                return None

            log.info('{}: the actor said {}'.format(actorKey, newKeyval))
            # called as callback, so the updated key is passed by default
            self.alertsActor.monitoring[actorKey].keyword = newKeyval
            self.alertsActor.monitoring[actorKey].checkKey()

        check([-9999], init=True)

        return check

    def updateKey(self, actorKey):
        def check(newKeyval):
            # print("---------------------------")
            # print(newKeyval)
            log.info('{}: the actor said {}'.format(actorKey, newKeyval))
            if len(newKeyval) == 1:
                newKeyval = newKeyval[0]
            # print("{} {} {}".format(actorKey, newKeyval, type(newKeyval)))
            # called as callback, so the updated key is passed by default
            self.alertsActor.monitoring[actorKey].keyword = newKeyval
            self.alertsActor.monitoring[actorKey].checkKey()

        return check

    def itsDeadJim(self, alertKey='NOT_SPECIFIED'):
        # some actor stopped outputting a keyword, raise the alarm!
        def setActive():
            self.alertsActor.monitoring[alertKey].setActive()

        return setActive


def staleCheck(keyState):
    """basically same as a heartbeat
    """
    if time.time() - keyState.lastalive < keyState.checkAfter:
        return "ok"
    elif time.time() - keyState.lastalive > 5*keyState.checkAfter:
        return "critical"
    else:
        return keyState.defaultSeverity
