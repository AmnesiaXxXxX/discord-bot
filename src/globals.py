from typing import List
import time
import threading
import logging
from loggers import waiting

yes = "✅"
no = "❌"


class WaitingAnswer(dict):
    def __init__(self) -> None:
        super().__init__()
        self.user_wait_timestamps: dict[int, float] = {}
        self.timeout: int = 60
        self.logger = waiting

        thr = threading.Thread(target=self.poll, daemon=True)
        thr.start()

    def __getitem__(self, index):
        return self.user_wait_timestamps[index]

    def __len__(self):
        return len(self.user_wait_timestamps)

    def __iter__(self):
        return iter(self.user_wait_timestamps)

    def add_user(self, user_id: int) -> None:
        if user_id not in self.user_wait_timestamps:
            self.user_wait_timestamps[user_id] = time.time()

    def remove_user(self, user_id: int) -> None:
        if user_id in self.user_wait_timestamps:
            self.user_wait_timestamps.pop(user_id)

    def is_waiting(self, user_id: int) -> bool:
        return user_id in self.user_wait_timestamps

    def poll(self):
        while True:
            self.logger.debug(self.user_wait_timestamps)
            with threading.Lock():
                for user_id in self._check_timeout(self.timeout):
                    self.remove_user(user_id)
            time.sleep(10)

    def _check_timeout(self, timeout: float) -> List[int]:
        now = time.time()
        return [
            user_id
            for user_id, timestamp in self.user_wait_timestamps.items()
            if now - timestamp > timeout
        ]
