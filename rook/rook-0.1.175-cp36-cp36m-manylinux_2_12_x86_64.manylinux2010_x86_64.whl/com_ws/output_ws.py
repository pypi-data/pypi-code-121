import logging
import time
import six
from rook import config
from rook.user_warnings import UserWarnings
from rook.com_ws.token_bucket import TokenBucket
from rook.protobuf.messages_pb2 import RuleStatusMessage, AugReportMessage, LogMessage
from rook.protobuf.variant_pb2 import Error
from rook.processor.namespace_serializer import NamespaceSerializer
from rook.processor.error import Error as RookError
from rook.processor.namespaces.container_namespace import ContainerNamespace
from rook.logger import logger


class Output(object):
    def __init__(self, agent_id):
        self._id = agent_id
        self._agent_com = None

        self._rule_status_updates_bucket = TokenBucket(config.OutputWsConfiguration.MAX_STATUS_UPDATES,
                                                       config.OutputWsConfiguration.BUCKET_REFRESH_RATE,
                                                       lambda: logger.error("Limit reached, dropping status updates"))

        self._user_message_bucket = TokenBucket(config.OutputWsConfiguration.MAX_AUG_MESSAGES,
                                                config.OutputWsConfiguration.BUCKET_REFRESH_RATE,
                                                lambda: logger.error("Limit reached, dropping aug report messages"))

        self._log_message_bucket = TokenBucket(config.OutputWsConfiguration.MAX_LOG_ITEMS,
                                               config.OutputWsConfiguration.BUCKET_REFRESH_RATE,
                                               lambda: self._internal_send_log_message(3,
                                                                                       time.time(),
                                                                                       __file__,
                                                                                       0,
                                                                                       "Limit reached, dropping log messages",
                                                                                       "Limit reached, dropping log messages"))
        logger.register_output(self)

    def set_agent_id(self, agent_id):
        self._id = agent_id

    def set_agent_com(self, agent_com):
        self._agent_com = agent_com

    def send_rule_status(self, rule_id, active, error):
        if not self._agent_com:
            return

        def send_msg():
            rule_status_message = RuleStatusMessage()
            rule_status_message.agent_id = self._id
            rule_status_message.rule_id = rule_id
            rule_status_message.active = active

            if error:
                rule_status_message.error.CopyFrom(self._convert_error(error.dumps()))

            self._agent_com.add(rule_status_message)
        self._rule_status_updates_bucket.do_if_available(send_msg)

    def send_user_message(self, aug_id, message_id, arguments):
        if not self._agent_com:
            return

        def send_msg():
            if arguments and arguments.size(''):
                if config.DumpConfig.PROTOBUF_VERSION_2:
                    error = self._agent_com.send_user_message(aug_id, message_id, arguments)
                    if error:
                        if not isinstance(error, RookError):
                            error = RookError(error)
                        UserWarnings.send_warning(error)
                else:
                    msg = AugReportMessage()
                    msg.agent_id = self._id
                    msg.aug_id = aug_id
                    msg.report_id = message_id

                    serializer = NamespaceSerializer(config.DumpConfig.STRING_CACHE_USERMESSAGE)
                    serializer.dump(arguments, msg.arguments)

                    for k, v in six.iteritems(serializer.get_string_cache()):
                        msg.strings_cache[k] = v

                    error = self._agent_com.add(msg)
                    if error:
                        UserWarnings.send_warning(RookError(error))
        self._user_message_bucket.do_if_available(send_msg)

    LOG_LEVELS = {
        logging.DEBUG: LogMessage.DEBUG,
        logging.INFO: LogMessage.INFO,
        logging.WARNING: LogMessage.WARNING,
        logging.ERROR: LogMessage.ERROR,
        logging.FATAL: LogMessage.FATAL
    }

    def send_log_message(self, level, time, filename, lineno, text, formatted_message, arguments):
        self._log_message_bucket.do_if_available(
            lambda: self._internal_send_log_message(level, time, filename, lineno, text, formatted_message, arguments)
        )

    def _internal_send_log_message(self, level, time, filename, lineno, text, formatted_message, arguments=None):
        # Until we clean up the initialization of AgentCom & Output (they used
        # to be codependent) we ignore logs from before the rook is actually
        # started
        if self._agent_com is None:
            return

        if arguments is None:
            arguments = {}

        msg = LogMessage()

        msg.timestamp.FromMilliseconds(int(time * 1000))
        msg.agent_id = self._id
        msg.level = level
        msg.filename = filename
        msg.line = lineno
        msg.text = str(text)
        msg.formatted_message = formatted_message
        if arguments:
            NamespaceSerializer().dump(ContainerNamespace(arguments), msg.legacy_arguments)

        self._agent_com.add(msg)

    def send_warning(self, rule_id, error):
        self.send_rule_status(rule_id, "Warning", error)

    def flush_messages(self):
        self._agent_com.flush_all_messages()

    def _convert_error(self, e):
        new_err = Error()
        new_err.message = e.message
        new_err.type = e.type
        new_err.parameters.CopyFrom(e.parameters)
        new_err.exc.CopyFrom(e.exc)
        new_err.traceback.CopyFrom(e.traceback)
        return new_err

    def is_user_messages_queue_full(self):
        return self._user_message_bucket.is_exhausted() or (self._agent_com is not None and self._agent_com.is_queue_full())
