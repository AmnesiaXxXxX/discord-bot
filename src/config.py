# Этот файл содержит настройки конфигурации, такие как токен бота и другие параметры.
import os
from dotenv import load_dotenv
import logging
import time
import threading

load_dotenv()


class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "None")
    PREFIX = "!"
    DEBUG: bool = bool(os.getenv("DEBUG", False))
    DATABASE_NAME = "database.db"

    def read(self):
        logger = logging.getLogger("config")

        # Перезагружаем переменные окружения
        load_dotenv(override=True)

        # Обновляем значения из .env
        for key, value in vars(Config).items():
            if not key.startswith("__"):
                # Если переменная есть в окружении, обновляем её значение
                if key in os.environ:

                    new_value = os.environ[key]
                    setattr(Config, key, new_value)
                    logger.debug(f"{key}: {str(value)[:10]} -> {str(new_value)[:10]}")

    def _start(self):
        while True:

            with threading.Lock():
                self.read()
            time.sleep(5)

    def start(self):

        thr = threading.Thread(target=self._start, daemon=True)
        thr.start()

    def update_debug_level(self, level: bool):
        logger = logging.getLogger("config")
        Config.DEBUG = level
        logger.setLevel(logging.DEBUG if level else logging.INFO)
        logger.info(f"Уровень отладки изменен на: {'DEBUG' if level else 'INFO'}")
