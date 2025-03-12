import os
from dotenv import load_dotenv
import logging
import time
import threading

load_dotenv()


class Config:

    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "None")
    PREFIX = "/"
    DEBUG: bool = bool(os.getenv("DEBUG", False))
    DATABASE_NAME = "database.db"

    def __init__(self) -> None:
        self._logger = logging.getLogger("discord")
        self.start()

    def read(self):
        load_dotenv(override=True)

        for key, value in vars(Config).items():
            if not key.startswith("__"):

                if key in os.environ:

                    new_value = os.environ[key]
                    setattr(Config, key, new_value)
                    self._logger.debug(
                        f"{key}: {str(value)[:10]} -> {str(new_value)[:10]}"
                    )

    def _start(self):
        while True:
            with threading.Lock():
                self.read()
            time.sleep(30)

    def start(self):
        thr = threading.Thread(target=self._start, daemon=True)
        thr.start()

    def update_debug_level(self, level: bool):
        Config.DEBUG = level
        self._logger.setLevel(logging.DEBUG if level else logging.INFO)
        self._logger.info(f"Уровень отладки изменен на: {'DEBUG' if level else 'INFO'}")
