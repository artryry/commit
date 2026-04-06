import logging
import json
import sys

from config import settings


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(log_record)


class Logger:
    __handler = logging.StreamHandler(sys.stdout)
    __handler.setFormatter(JsonFormatter())

    __logger = logging.getLogger("auth_service")
    __logger.setLevel(settings.LOG_LVL)
    __logger.addHandler(__handler)

    @classmethod
    def info(cls, message: str):
        cls.__logger.info(message)

    @classmethod
    def error(cls, message: str):
        cls.__logger.error(message)

    @classmethod
    def debug(cls, message: str):
        cls.__logger.debug(message)

    @classmethod
    def warning(cls, message: str):
        cls.__logger.warning(message)

    @classmethod
    def critical(cls, message: str):
        cls.__logger.critical(message)
