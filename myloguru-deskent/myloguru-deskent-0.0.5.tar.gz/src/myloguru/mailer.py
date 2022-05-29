from .my_loguru import logger, MyLogger


class MailerLogger(MyLogger):
    """Add new methods for default loguru.logger"""

    def admin(self, text, *args, **kwargs):
        self._logger.log("ADMIN", text, *args, **kwargs)

    def token(self, text, *args, **kwargs):
        self._logger.log("TOKEN", text, *args, **kwargs)

    def openai(self, text, *args, **kwargs):
        self._logger.log("OPENAI", text, *args, **kwargs)

    def get_new_logger(self) -> 'MailerLogger':
        self.add_level("ADMIN", "<fg #d787ff>", no=100)
        self.add_level("TOKEN", "<white>", no=90)
        self.add_level("OPENAI", "<fg #d787ff>", no=80)
        self.add_logger(enqueue=True, level='WARNING', rotation="50 MB")
        self.add_logger(enqueue=True, level='WARNING', rotation="50 MB", serialize=True)
        self.add_logger(enqueue=True, level='ADMIN', rotation="100 MB")
        self.add_logger(enqueue=True, level='TOKEN', rotation="50 MB")
        self.add_logger(enqueue=True, level='OPENAI', rotation="50 MB")

        return self


logger: MailerLogger = MailerLogger(logger).get_new_logger()
