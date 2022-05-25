#!/usr/bin/env python
# encoding: utf-8
#
# dangerKey.py
#
# Created by John Donor on 10 April 2019

import re, time
from yaml import YAMLObject

from alertsActor import log


class diskCheck(YAMLObject):
    """evaluate a disk keyword
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        """The keyval is an enum ('Ok','Warning','Serious','Critical')
        and the amount of free space (GB)
        """
        keyval = keyState.keyword
        if (keyval[0]).upper() == 'OK':
            return "ok"
        elif (keyval[0]).upper() == 'WARNING':
            return "warn"
        elif (keyval[0]).upper() == 'SERIOUS':
            return "serious"
        elif (keyval[0]).upper() == 'CRITICAL':
            return "critical"
        else:
            return "info"


class doNothing(object):
    """camcheck alerts can't check themselves

       dummy class to facilitate that
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        return keyState.severity


class camCheck(YAMLObject):
    """evaluate a camCheck alert
    """
    def __init__(self):
        # NEVER GETS CALLED!!!! -_-
        pass

    def generateCamCheckAlert(self, key, severity):
        inst = key[:3]
        side = key[3]
        key = "camCheck." + key
        instruments = ["boss"]

        # most keywords will be SP[12][RB]
        # check if they are and assign appropriate instruments
        if inst in ["SP1", "SP2"]:
            instruments.append("boss.{}".format(inst))
            if side in ["R", "B"]:
                instruments.append("boss.{}.{}".format(inst, side))

        if severity in ["critical", "serious"]:
            selfClear = False
            addresses = self.emailAddresses
        else:
            selfClear = True
            addresses = None

        if key not in self.triggered:
            self.triggered.append(key)

        if key not in self.alertsActor.monitoring:
            dumbCheck = doNothing()
            self.alertsActor.addKey(key, severity=severity, checkAfter=120,
                                    selfClear=selfClear, checker=dumbCheck,
                                    keyword="'Reported by camCheck'",
                                    instruments=instruments, emailAddresses=addresses,
                                    emailDelay=0)
        if self.alertsActor.monitoring[key].active:
            self.alertsActor.monitoring[key].stampTime()
        else:
            self.alertsActor.monitoring[key].setActive(severity)

    def __call__(self, keyState):
        keyval = keyState.keyword
        if self.alertsActor is None:
            print("setting alertsActor for camCheck!!")
            self.alertsActor = keyState.alertsActorReference
            # do this only once hopefully
            for i in ["boss.SP1", "boss.SP2", "boss.SP1.R", "boss.SP2.R",
                      "boss.SP1.B", "boss.SP2.B"]:
                self.alertsActor.instrumentDown[i] = False
        # print("CAMCHECK, len {}, type {}, key: {}".format(len(keyval), type(keyval), keyval))
        log.info('CAMCHECK reported {}'.format(keyval))

        if type(keyval) == str:
            # could possibly try to fix this in hubModel casts, but easier here
            keyval = [keyval]
        if len(keyval) == 1 and keyval[0] == "None": # this is a bug somewhere upstream
            keyval = []
        for k in keyval:
            if re.search(r"SP[12][RB][0-3]?CCDTemp", k):
                self.generateCamCheckAlert(k, "critical")
            elif re.search(r"SP[12]SecondaryDewarPress", k):
                self.generateCamCheckAlert(k, "critical")
            elif re.search(r"SP[12](DAQ|Mech|Micro)NotTalking", k):
                self.generateCamCheckAlert(k, "critical")
            elif re.search(r"DACS_SET", k):
                self.generateCamCheckAlert(k, "critical")
            elif re.search(r"SP[12]LN2Fill", k):
                self.generateCamCheckAlert(k, "serious")
            elif re.search(r"SP[12](Exec|Phase)Boot", k):
                self.generateCamCheckAlert(k, "serious")
            else:
                self.generateCamCheckAlert(k, "warn")

        for k in self.triggered:
            if k.split(".")[-1] not in keyval:  # b/c we know its camCheck already
                self.alertsActor.monitoring[k].severity = "ok"
                # now it can check itself and find out its cool
                # and then decide to disappear if its acknowledged, etc etc
                self.alertsActor.monitoring[k].checkKey()
                self.triggered.remove(k)

        # never flag camCheck, always monitored keys
        return "ok"


class heartbeatCheck(YAMLObject):
    """check a heartbeat.
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        if time.time() - keyState.lastalive < keyState.checkAfter:
            return "ok"
        elif time.time() - keyState.lastalive > 5*keyState.checkAfter:
            return "critical"
        else:
            return keyState.defaultSeverity


class above(YAMLObject):
    """literally: is the value too high
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        if keyState.keyword > keyState.dangerVal:
            return keyState.defaultSeverity
        else:
            return "ok"


class below(YAMLObject):
    """literally: is the value too low
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        if keyState.keyword < keyState.dangerVal:
            return keyState.defaultSeverity
        else:
            return "ok"


class neq(YAMLObject):
    """literally: is the value too low
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        if keyState.keyword != keyState.dangerVal:
            return keyState.defaultSeverity
        else:
            return "ok"


class inList(YAMLObject):
    """is any value in the list "True", e.g. flagged
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        if [k for k in keyState.keyword if k]:
            return keyState.defaultSeverity
        else:
            return "ok"


class firstElem(YAMLObject):
    """is any value in the list "True", e.g. flagged
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        if keyState.keyword[0] == keyState.dangerVal:
            return keyState.defaultSeverity
        else:
            return "ok"


class default(object):
    """check equality to a dangerval
    """
    def __init__(self):
        pass

    def __call__(self, keyState):
        if keyState.keyword == keyState.dangerVal:
            return keyState.defaultSeverity
        else:
            return "ok"
