import sys

import zhmcclient

from chaoslib.exceptions import InterruptExecution

from logzero import logger


class Send_Command():
    """
    Send a command to z/OS.  Because there are a bunch of different ways to do this,
    this gets sort of ugly.
    May want to abstract this to its own class/library at some point.
    """

    def __init__(self, location: str = None, connection_information: dict = None,
                 command_to_send=None, message_to_watch_for=None):

        """
        Sends a command to z/OS
        :param location:  This is the place to send the command to.  Format will differ
        based on method
        :param connection_information:  This is information on how to connect to the
        method you're sending the command to.
        :param command_to_send:  The command to send.
        :param message_to_watch_for: A message id to look for, if a response is expected

        """

        if command_to_send is None:
            raise EmptyCommand

        self.command_to_send = command_to_send
        self.message_to_watch_for = message_to_watch_for
        self.message_out = list()

        if connection_information["method"] == "hmc":

            # Print metadata for each OS message, before each message
            PRINT_METADATA = False

            hmc = connection_information["hostname"]
            userid = connection_information["userid"]
            password = connection_information["password"]

            logger.debug("Trying to connect to HMC %s with userid %s" % (hmc, userid))

            try:
                session = zhmcclient.Session(hmc, userid, password)
            except zhmcclient.ConnectionError:
                logger.error("Unable to connect to HMC %s" % hmc)
                raise InterruptExecution("Unable to connect to HMC %s" % hmc)

            cpcname = connection_information["cpc_name"]
            partname = connection_information["partition_name"]

            cl = zhmcclient.Client(session)

            try:
                cpc = cl.cpcs.find(name=cpcname)
            except zhmcclient.NotFound:
                raise InterruptExecution("Could not find CPC %s on HMC %s" %
                                         (cpcname, hmc))

            try:
                if cpc.dpm_enabled:
                    partkind = "partition"
                    partition = cpc.partitions.find(name=partname)
                else:
                    partkind = "LPAR"
                    partition = cpc.lpars.find(name=partname)
            except zhmcclient.NotFound:
                raise InterruptExecution("Could not find %s %s on CPC %s" %
                                         (partkind, partname, cpcname))

            logger.info("Sending command %s for %s %s on CPC %s ..." %
                        (command_to_send, partkind, partname, cpcname))

            if message_to_watch_for is not None:
                topic = partition.open_os_message_channel(include_refresh_messages=True)
                logger.debug("OS message channel topic: %s" % topic)

                receiver = zhmcclient.NotificationReceiver(topic, hmc, userid, password)
                logger.debug("Showing OS messages (including refresh messages) ...")
                sys.stdout.flush()

            try:
                partition.send_os_command(command_to_send)
            except zhmcclient.Error:
                raise InterruptExecution("Command failed")

            if message_to_watch_for is not None:
                try:
                    for headers, message in receiver.notifications():
                        os_msg_list = message['os-messages']
                        for os_msg in os_msg_list:
                            if PRINT_METADATA:
                                msg_id = os_msg['message-id']
                                held = os_msg['is-held']
                                priority = os_msg['is-priority']
                                prompt = os_msg.get('prompt-text', None)
                                logger.debug("# OS message %s (held: %s, priority: %s, "
                                             "prompt: %r):" %
                                             (msg_id, held, priority, prompt))
                            msg_txt = os_msg['message-text'].strip('\n')
                            os_msg_id = msg_txt.split()[0]
                            sys.stdout.flush()
                            if os_msg_id == message_to_watch_for:
                                self.message_out = msg_txt.splitlines()
                                raise NameError
                except KeyboardInterrupt:
                    logger.debug("Keyboard interrupt - leaving receiver loop")
                    sys.stdout.flush()
                except NameError:
                    logger.debug("Message with ID %s occurred - leaving receiver loop" %
                                 message_to_watch_for)
                    sys.stdout.flush()
                finally:
                    logger.info("Closing receiver...")
                    sys.stdout.flush()
                    receiver.close()

            logger.info("Logging off...")
            sys.stdout.flush()
            session.logoff()

        elif connection_information["method"] == "ssh":

            from paramiko import SSHClient, SSHException

            hostname = connection_information["hostname"]
            userid = connection_information["userid"]
            password = connection_information.get("password")

            try:
                client = SSHClient()
                client.load_system_host_keys()
                client.connect(hostname=hostname, username=userid, password=password)
            except SSHException:
                logger.warning("SSH Exception")
                raise ()

            string_to_send = ('bash -l -c \'opercmd -- \"%s\"\'' % self.command_to_send)

            logger.debug(string_to_send)

            stdin, stdout, stderr = client.exec_command(string_to_send)

            for line in stdout:
                self.message_out.append(line.rstrip())

            logger.debug(self.message_out)

            client.close()

            self.message_out.pop(0)
            self.message_out.pop(0)

        else:
            raise InterruptExecution("Invalid connection method specified")


class TimeoutException(Exception):
    """
    Raised when a command can't be sent in a given time

    """


class EmptyCommand(Exception):
    """
    Raised when no command string is given
    """
