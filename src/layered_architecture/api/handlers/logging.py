from logging import config

from layered_architecture.config.settings import settings


def configure_logging() -> None:
    """
    Configures application logging using settings from config.
    """
    config.dictConfig(settings.LOGGING_CONFIG)
