###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""NagiosConnector is a utility to publish checks on job results to the IT-
based SAM/Nagios framework.

The publishing is done by messaging via an ActiveMQ-Broker specified in
the configuration (It expects values for MsgBroker, MsgPort,  MsgQueue
and NagiosName). For the message to arrive, it is essential to publish
to the right queue, which is also specified in the configuration. The
message is built using a dictionary passed to one of the methods, which
should contain the keys 'SAMResults' 'SAMDetails' 'GridRequiredCEs'.
"""
import datetime
import stomp

from DIRAC import gLogger, gConfig
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations


class NagiosConnector(object):
    """Bundles functions in the stomp library for sending SAMJob-Results to SAM-
    Nagios."""

    def __init__(self):
        self.config = {}
        self.opsHelper = Operations()
        self.conn = None
        self.message = ""

    def readConfig(self):
        """get Message Broker and Queue from Configuration file."""

        self.config = {}
        for item in ["MsgBroker", "MsgQueue", "MsgPort"]:
            path = self.opsHelper.getPath("/NagiosConnector/%s" % item)
            self.config[item] = gConfig.getValue(path)
            if not self.config[item]:
                gLogger.verbose("Required Configuration Value is empty: %s" % item)
            else:
                gLogger.verbose("Read Config Values for %s: %s" % (item, self.config[item]))

        try:
            self.config["MsgPort"] = int(self.config["MsgPort"])
        except (TypeError, ValueError):
            self.config["MsgPort"] = 6163

    def useDebugMessage(self):
        """Load a sample message for debugging."""
        self.message = """hostName: ce.hpc.iit.bme.hu
metricStatus: OK
timestamp: 2013-11-09T17:59:19Z
nagiosName: org.lhcb.DiracTest-lhcb
summaryData: publishing by Dirac successful
serviceURI:   ce.hpc.iit.bme.hu
serviceFlavour: CE
siteName: myTestSite
metricName: org.lhcb.DiracTest
gatheredAt: sam-developers-machine
role: site
voName: lhcb
serviceType: org.lhcb.CE
detailsData: further details here:
EOT"""

    def assembleMessage(
        self,
        serviceURI="no serviceURI given",
        status="no status given",
        details="no details given",
        nagiosName="no nagiosName given",
    ):
        """Brings message information to the generic format required by Nagios."""

        statuscodes = {0: "OK", 1: "CRITICAL", 2: "WARNING", 3: "UNKNOWN"}
        if status in ["CRITICAL", "OK", "WARNING", "UNKNOWN"]:
            pass
        elif status in range(4):
            status = statuscodes[status]

            currentTime = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            message = ""
            message += "serviceURI: %s\n" % serviceURI
            message += "metricStatus: %s\n" % status
            message += "timestamp: %s\n" % currentTime
            message += "nagiosName: %s\n" % nagiosName
            message += "summaryData: %s\n" % details
            # all other fields are not used in SAM-Nagios
            # they are left here for compatibility / legacy
            # message += "gatheredAt: %s\n" % msginfos['ce']
            # message += "metricName: org.lhcb.WN-%s-lhcb\n" % msginfos[ 'JobName' ]
            # message += "serviceFlavour: %s\n" % msginfos['serviceFlavour']
            # message += "role: site\n"
            # message += "voName: lhcb\n"
            # message += "serviceType: org.lhcb.WN\n"
            # message += "detailsData: %s\n" % msginfos[ 'testDetails' ]
            message += "EOT\n"
            self.message = message

    def initializeConnection(
        self, _use_ssl=False, _ssl_key_file=None, _ssl_cert_file=None, _ssl_ca_certs=None, _ssl_cert_validator=None
    ):
        """Connect the conn object with the Broker read from configuration.

        Refer to the stomppy documentation for full authentication args details.

        :param _use_ssl:  connect using SSL to the socket.
          This wraps the socket in a SSL connection.
          The constructor will raise an exception if you ask for SSL,
          but it can't find the SSL module.
        :param _ssl_cert_file:  the path to a X509 certificate
        :param _ssl_key_file: the path to a X509 key file
        :param _ssl_ca_certs:  the path to the a file containing CA certificates to validate the server against.
        :param _ssl_cert_validator:  function which performs extra validation on the client certificate
        """
        try:
            self.conn = stomp.Connection(
                [(self.config["MsgBroker"], self.config["MsgPort"])],
            )
            self.conn.set_ssl(
                use_ssl=_use_ssl,
                ssl_key_file=_ssl_key_file,
                ssl_cert_file=_ssl_cert_file,
                ssl_ca_certs=_ssl_ca_certs,
                ssl_cert_validator=_ssl_cert_validator,
            )
            # There may be a need to receive messages.
            # In this case there should be a class with an on_message method
            # conn.set_listener('',MyListener()) python-messaging provides a useful class.
            self.conn.connect()
        except stomp.exception.ConnectFailedException as e:
            gLogger.error("Error establishing connection: %s" % e)

    def sendMessage(self):
        """Use the conn object to send a message to the broker.

        If the format and the configurations are correct, the message
        content will appear in SAM/Nagios.
        """

        if not self.message:
            gLogger.error("The message string is empty!")
        self.conn.send(destination=self.config["MsgQueue"], body=self.message)
        gLogger.verbose("Message sent to %s on %s" % (self.config["MsgBroker"], self.config["MsgQueue"]))
        gLogger.verbose("Message content %s" % self.message)

    def endConnection(self):
        """Call disconnect() on the conn object."""
        self.conn.disconnect()
        gLogger.verbose("Connection successfully terminated")
