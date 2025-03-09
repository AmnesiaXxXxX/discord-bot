import logging
import os
import gzip
import atexit
import datetime


def get_console_handler():
    """Создает и настраивает консольный обработчик, если он не существует."""
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    return console_handler


def get_file_handler():
    """Создает и настраивает обработчик для записи логов в файл."""
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_handler = logging.FileHandler(os.path.join(log_dir, "latest.log"), mode="a")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    return file_handler


def setup_discord_loggers():
    """Настраивает все логгеры, связанные с discord, чтобы предотвратить дублирование"""
    discord_logger = logging.getLogger("discord")
    discord_logger.handlers = []
    discord_logger.propagate = False
    discord_logger.addHandler(get_console_handler())
    discord_logger.addHandler(get_file_handler())

    for name in ["discord.client", "discord.gateway", "discord.voice_client"]:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = False
        logger.addHandler(get_console_handler())
        logger.addHandler(get_file_handler())


def setup_logger(name: str) -> logging.Logger:
    """Настраивает логгер с консольным и файловым обработчиками."""
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    return logger


def compress_latest_log():
    """При завершении работы зашифровывает лог в gzip архив с названием datetime.log.gz"""
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    latest_log_path = os.path.join(log_dir, "latest.log")
    if os.path.exists(latest_log_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(log_dir, f"{timestamp}.log.gz")
        with open(latest_log_path, "rb") as f_in:
            with gzip.open(output_file, "wb") as f_out:
                f_out.writelines(f_in)


atexit.register(compress_latest_log)

setup_discord_loggers()

main = setup_logger(__name__)
config = setup_logger("config")
waiting = setup_logger("waiting")

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
