import logging

def get_console_handler():
    """Создает и настраивает консольный обработчик, если он не существует."""
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    return console_handler

def setup_discord_loggers():
    """Настраивает все логгеры, связанные с discord, чтобы предотвратить дублирование"""
    discord_logger = logging.getLogger("discord")
    discord_logger.handlers = []
    discord_logger.propagate = False
    discord_logger.addHandler(get_console_handler())

    for name in ["discord.client", "discord.gateway", "discord.voice_client"]:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = False
        logger.addHandler(get_console_handler())

def setup_logger(name: str) -> logging.Logger:
    """Настраивает логгер с единственным консольным обработчиком."""
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(get_console_handler())
    return logger


setup_discord_loggers()


main = setup_logger(__name__)
config = setup_logger("config")
waiting = setup_logger("waiting")


root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
