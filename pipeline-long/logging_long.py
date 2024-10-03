"""A file to set up logging configuration."""
import logging

LOG_FORMAT = "%(asctime)s %(levelname)s %(message)s"


def logger_setup(log_filename: str, log_folder: str, loglevel=logging.INFO) -> None:
    """Creates and configures the root logger for this module."""

    logging.basicConfig(format=LOG_FORMAT,
                        filename=f"{log_folder}/{log_filename}",
                        level=loglevel,
                        encoding="UTF-8",
                        filemode='a')


if __name__ == "__main__":

    logger_setup("test_logs.log", "logs")
    LOGGER = logging.getLogger(__name__)
    LOGGER.info("testing logger is working")
