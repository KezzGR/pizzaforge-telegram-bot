import logging

from config import settings


def setup_logger():
    """Настраивает логирование приложения в stdout контейнера."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=log_level,
        handlers=[logging.StreamHandler()],
    )

    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    return logging.getLogger(__name__)


logger = setup_logger()
