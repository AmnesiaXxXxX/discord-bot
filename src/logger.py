import logging

discord_logger = logging.getLogger("discord")
discord_handler = discord_logger.handlers[0] if discord_logger.handlers else None
discord_formatter = discord_handler.formatter if discord_handler else None

config = logging.getLogger("config")
handler = logging.StreamHandler()
handler.setFormatter(discord_formatter)


config.addHandler(handler)
