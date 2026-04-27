import logging
import sys

from config import cfg

LOG_FORMAT = (
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

def setup_logger(log_level):
    logging.basicConfig(
        level=log_level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    return logging.getLogger()


def get_logging_level():
    match cfg.LOGGING_LEVEL:
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO


Logger = setup_logger(get_logging_level())
