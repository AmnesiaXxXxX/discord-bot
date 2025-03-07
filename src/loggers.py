import logging

def get_console_handler():
    """Create and configure console handler if it doesn't exist."""
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    return console_handler

def setup_discord_loggers():
    """Setup all discord-related loggers to prevent duplication"""
    discord_logger = logging.getLogger("discord")
    discord_logger.handlers = []
    discord_logger.propagate = False
    discord_logger.addHandler(get_console_handler())
    
    # Настраиваем дочерние логгеры discord
    for name in ["discord.client", "discord.gateway", "discord.voice_client"]:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = False
        logger.addHandler(get_console_handler())

def setup_logger(name: str) -> logging.Logger:
    """Set up a logger with single console handler."""
    logger = logging.getLogger(name)
    logger.handlers = []
    logger.propagate = False
    logger.addHandler(get_console_handler())
    return logger

# Настраиваем логгеры
setup_discord_loggers()

# Инициализируем остальные логгеры
main = setup_logger(__name__)
config = setup_logger("config")
waiting = setup_logger("waiting")

# Устанавливаем уровень для корневого логгера
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
