#!/usr/bin/env python
# encoding: utf-8
#
# alerts_main.py
#


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import json
# import yaml
import sys
import os
import traceback

import time

from click.testing import CliRunner

from opscore.RO.StringUtil import strFromException
from opscore.RO.Comm.TwistedTimer import Timer
from opscore.utility.qstr import qstr
from twistedActor import BaseActor, CommandError, UserCmd

from alertsActor import __version__, alertActions
from alertsActor.cmds.cmd_parser import alerts_parser
from alertsActor import log

from alertsActor.rules import callbackWrapper, mail, dangerKey  # sms


class alertsActor(BaseActor):
    """the actor"""

    def __init__(self, config, **kwargs):

        self.cmdParser = alerts_parser
        self.config = config

        super(alertsActor, self).__init__(**kwargs)

        # a dictionary of actor keys we're watching
        self.monitoring = dict()

        # keep track of downed instruments
        # since its either up or down, make boolean
        # UP = False, DOWN = True
        self.instrumentDown = dict()

        # keep track of heartbeats
        self.heartbeats = dict()

        self.callbacks = callbackWrapper.wrapCallbacks(self, alertActions)

        self.connectHub('localhost', datamodel_casts=self.callbacks.datamodel_casts,
                                     datamodel_callbacks=self.callbacks.datamodel_callbacks)

        logfile = os.path.join(self.config["logging"]["logdir"],
                               time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()))
        log.start_file_logger(logfile + ".log")

        log.info('starting alertsActor actor version={!r} in port={}'
                 .format(__version__, kwargs['userPort']))

    def addKey(self, key, severity, **kwargs):
        self.monitoring[key] = keyState(self, actorKey=key, severity=severity, **kwargs)

    @property
    def activeAlerts(self):
        active = []
        for k, a in self.monitoring.items():
            if a.active:
                active.append(a)

        return active

    @property
    def disabledAlerts(self):
        disabled = []
        for k, a in self.monitoring.items():
            if a.disabled:
                disabled.append(a)

        return disabled

    def broadcastActive(self):
        activeMessage = "activeAlerts{}".format(("=" if len(self.activeAlerts) else "")) +\
                       ", ".join(["{}".format(a.actorKey) for a in self.activeAlerts])
        self.writeToUsers("i", activeMessage)

    def broadcastDisabled(self):
        disabledMessage = "disabledAlertRules{}".format(("=" if len(self.disabledAlerts) else "")) +\
                       ", ".join(['"({}, {}, {})"'.format(a.actorKey, a.severity, a.disabledBy)
                                  for a in self.disabledAlerts])
        self.writeToUsers("i", disabledMessage)

    def broadcastAll(self):
        for a in self.activeAlerts:
            a.dispatchAlertMessage()

    def broadcastInstruments(self):
        instruments = list()
        for k, a in self.monitoring.items():
            if a.instruments is not None:
                for i in a.instruments:
                    if i not in instruments:
                        instruments.append(i)
        down = [i for i in instruments if self.instrumentDown[i]]
        self.writeToUsers("i", 'instrumentNames={}'.format(",".join(instruments)))
        self.writeToUsers("i", 'downInstruments={}'.format(",".join(down)))

    def reconnect(self):
        # convenience method to call occassionally
        # should be able to recover from a hub disconnect
        if self.hub is None:
            print("no hub connection, reconnecting!")
            self.connectHub('localhost', datamodel_casts=self.callbacks.datamodel_casts,
                                         datamodel_callbacks=self.callbacks.datamodel_callbacks)
        elif self.hub.didFail:
            print("no hub connection, reconnecting!")
            self.connectHub('localhost', datamodel_casts=self.callbacks.datamodel_casts,
                                         datamodel_callbacks=self.callbacks.datamodel_callbacks)

    @property
    def hubModel(self):
        # keeps a running data model of keywords coming from the hub
        # allows callbacks on updates

        # this may need to be more careful... test!
        self.reconnect()

        return self.hub.datamodel

    def parseAndDispatchCmd(self, cmd):
        """Dispatch the user command. Stolen from BMO."""

        def test_cmd(args):
            # print("t ", args)
            result = CliRunner().invoke(alerts_parser, args)
            if result.exit_code > 0:
                # If code > 0, there was an error. We fail the command and inform the users.
                textMsg = result.output
                for line in textMsg.splitlines():
                    line = json.dumps(line).replace(';', '')
                    cmd.writeToUsers('w', 'text={0}'.format(line))
                cmd.setState(cmd.Failed)
                return False
            else:
                if '--help' in args:
                    # If help was in the args, we just want to print the usage to the users.
                    textMsg = result.output
                    for line in textMsg.splitlines():
                        line = json.dumps(line).replace(';', '')
                        cmd.writeToUsers('w', 'text={0}'.format(line))
                    cmd.setState(cmd.Done)
                    return False

                return True

        if not cmd.cmdBody:
            # echo to show alive
            self.writeToOneUser(":", "", cmd=cmd)
            return

        cmd.setState(cmd.Running)

        try:
            # stui wants to pass keyword args, parse doesn't support that
            # this is definitely bad form, but we're trying not to change
            # stui yet
            # click is case sensetive and requires lower-case -_-
            # except keywords are often camelCase. Ugh.... Starting to dislike click
            args = [a.lower() if not "=" in a else a for a in cmd.cmdBody.split()]
            args = [a.split("=")[-1] for a in args]
            # current tron config passes user, we aren't handling that yet
            # print("cmd", cmd.__dict__)
            # print(args)
            if "." in args[0]:
                user = args[0]
                cmd.cmdID = int(args[1])
                temp_args = args[2:]
            else:
                # user = "?.?"
                user = f"{cmd.userID}.{cmd.cmdID}"
                temp_args = args
            args = temp_args
            # user = f"{cmd.userID}.{cmd.cmdID}"
            log.info('{} issued {}'.format(user, args))
            result = test_cmd(args)
            if result is False:
                return
            # cmd.cmdBody = " ".join(temp_args)
            alerts_parser(args, obj=dict(actor=self, cmd=cmd, user=user))
        except CommandError as ee:
            log.warning("command {} failed with {}".format(cmd.cmdStr, strFromException(ee)))
            cmd.setState('failed', textMsg=strFromException(ee))
            return
        except Exception as ee:
            sys.stderr.write('command {0!r} failed\n'.format(cmd.cmdStr))
            traceback.print_exc(file=sys.stderr)
            textMsg = strFromException(ee)
            hubMsg = 'Exception={0}'.format(ee.__class__.__name__)
            log.warning("command {} failed with {}".format(cmd.cmdStr, strFromException(ee.__class__.__name__)))
            cmd.setState("failed", textMsg=textMsg, hubMsg=hubMsg)
        except BaseException:
            # This catches the SystemExit that Click insists in returning.
            pass


def ack(acknowledged):
    if acknowledged:
        return "ack"
    else:
        return "noack"


def enabled(disabled):
    if disabled:
        return "disabled"
    else:
        return "enabled"


def parseKey(keyVal):
    """readable keyVal"""
    if type(keyVal) is list:
        return "[{}]".format("".join(["{}.".format(i) for i in keyVal]))
    else:
        return str(keyVal)


class keyState(object):
    '''Keep track of the state of each actor.key'''

    def __init__(self, alertsActor, actorKey='oop.forgot', keyword="",
                 emailAddresses=None, **kwargs):
        self.alertsActorReference = alertsActor
        self.triggeredTime = None
        self.actorKey = actorKey
        self.keyword = keyword
        self.lastalive = time.time()  # updated for heartbeats
        self.active = False
        self.disabled = False
        self.disabledBy = -1
        self.severity = "ok"
        self.acknowledged = False
        self.acknowledgeMsg = ""
        self.acknowledger = -1
        self.checkMe = Timer()
        self.emailTimer = Timer()
        self.emailAddresses = emailAddresses
        self.emailSent = False
        # self.smtpclient = "localhost:1025"
        self.smtpclient = alertsActor.config["email"]["mailClient"]

        # kwargs, second argument is the default
        self.defaultSeverity = kwargs.get("severity", "info")
        self.dangerVal = kwargs.get("dangerVal", None)
        self.selfClear = kwargs.get("selfClear", False)
        self.instruments = kwargs.get("instruments", None)
        self.checkAfter = kwargs.get("checkAfter", 120)
        self.checker = kwargs.get("checker", dangerKey.default())
        self.emailDelay = kwargs.get("emailDelay", self.checkAfter)

        assert self.severity in ['ok', 'info', 'apogeediskwarn', 'warn', 'serious', 'critical'], "severity level not allowed"

    def keywordFmt(self):
        if "heartbeat" in self.actorKey:
            instring = "at {time}; last seen {diff} sec ago".format(time=self.triggeredTime,
                                                                    diff=int(time.time()-self.lastalive))
        elif "stale" in self.actorKey:
            instring = "at {time}; no change for {diff} sec, with {keyword}".format(time=self.triggeredTime,
                                                                    diff=int(time.time()-self.lastalive),
                                                                    keyword=parseKey(self.keyword))
        else:
            instring = 'at {time} UT found {keyword}'.format(keyword=parseKey(self.keyword), time=self.triggeredTime)
        return qstr(instring)

    @property
    def msg(self):
        return "alert={actorKey}, {severity}, {value}, {enable}, {acknowledged}, {acknowledger}".format(
               actorKey=self.actorKey, value=self.keywordFmt(),
               severity=self.severity, enable=enabled(self.disabled), acknowledged=ack(self.acknowledged),
               acknowledger=self.acknowledger)

    @property
    def instDown(self):
        if self.instruments is None:
            return False

        for i in self.instruments:
            if self.alertsActorReference.instrumentDown[i]:
                return True
        else:
            return False

    def stampTime(self):
        self.triggeredTime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    def setActive(self, severity=None):
        # something cause a problem, do stuff
        self.acknowledged = False  # clear anything from old alert
        self.active = True
        if severity is None:
            self.severity = self.defaultSeverity
        else:
            self.severity = severity
        self.stampTime()
        self.checkMe.start(self.checkAfter, self.reevaluate)

        if self.instDown:
            self.disable(0)
            log.info("NO ALERT: {} instrument down, no alert!!".format(self.actorKey))
            return None

        self.dispatchAlertMessage()
        # give the alert a chance to clear before emailing everyone
        self.emailTimer.start(self.emailDelay, self.sendEmail)

    def clear(self):
        # everything good, back to normal
        self.active = False
        self.checkMe.cancel()
        self.checkMe = Timer()
        self.emailTimer.cancel()
        self.emailTimer = Timer()
        self.severity = 'ok'
        self.triggeredTime = None
        self.emailSent = False

        self.alertsActorReference.broadcastActive()
        self.alertsActorReference.broadcastDisabled()
        self.alertsActorReference.broadcastAll()

    def acknowledge(self, msg=None, acknowledgedBy=None, unack=False):
        if msg is not None:
            self.acknowledgeMsg += msg + ";" # so we can add many... I guess?

        if acknowledgedBy is not None:
            self.acknowledger = acknowledgedBy

        if unack:
            self.acknowledged = False
        else:
            self.acknowledged = True

        self.dispatchAlertMessage()

    def reevaluate(self):
        # at some point this will presumably raise alert level?
        # possibly send email? Or only send email for critical? Or...
        if self.alertsActorReference.hub.didFail:
            self.alertsActorReference.reconnect()
        check = self.checkKey()
        print("evaluated {} found {} default {}".format(self.actorKey, check, self.defaultSeverity))
        if check != self.severity:
            # something changed, treat it like new alert
            self.severity = check
            self.acknowledge(acknowledgedBy=0, unack=True)
            self.dispatchAlertMessage()
        if not self.active:
            return

        if self.acknowledged:
            # keep checking myself until I go away
            self.checkMe.start(self.checkAfter, self.reevaluate)
            return

        if self.disabled:
            self.checkMe.start(self.checkAfter, self.reevaluate)
            return

        self.dispatchAlertMessage()
        self.checkMe.start(self.checkAfter, self.reevaluate)

    def sendEmail(self):
        # notify over email
        if self.emailAddresses is None or self.disabled:
            return

        if self.emailSent:
            # I don't think this should happen but it seems to...
            log.info("Tried to send extra email for {}".format(self.actorKey))
            return

        if not self.active:
            log.warn("Tried to send email after clear for {}".format(self.actorKey))
            return

        mail.sendEmail(self, self.smtpclient)
        # and sms?
        # sms.sendSms(self)  # just a reminder for later , phoneNumbers=["+18177733196"])
        self.emailSent = True

    def dispatchAlertMessage(self):
        # write an alert to users

        if self.severity == 'critical':
            broadcastSeverity = 'e'
        elif self.severity == 'warn' or self.severity == 'serious':
            broadcastSeverity = 'w'
        else:
            broadcastSeverity = 'i'

        self.alertsActorReference.writeToUsers(broadcastSeverity, self.msg)

        log.info("ALERT! " + self.msg)

    def checkKey(self):
        # check key, should be called when keyword changes

        check = self.checker(self)

        if check == "ok":
            if self.selfClear:
                self.clear()
            elif self.acknowledged:
                self.clear()
            else:
                # self.severity = "ok"
                return self.severity
        else:
            if not self.active:
                self.setActive(check)

        return check

    def disable(self, disabledBy):
        self.disabled = True
        self.disabledBy = disabledBy

        # self.active = False

        # probably do some more stuff

    def enable(self):
        self.disabled = False
        self.checkKey()
